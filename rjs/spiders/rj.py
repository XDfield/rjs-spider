# -*- coding: utf-8 -*-
import re

import scrapy
import pymongo

from rjs.items import TVShow, Resource
from rjs.loaders import MyLoader


BASE_URL = 'http://www.zhuixinfan.com/viewtvplay-{}.html'


class RjSpider(scrapy.Spider):
    name = 'rj'
    allowed_domains = ['www.zhuixinfan.com']

    def __init__(self, bPage=1, errLimit=100, mode='inc', *args, **kwargs):
        super(RjSpider, self).__init__(*args, **kwargs)
        self.errLimit = errLimit
        self.errCount = 0
        self.bPage = bPage
        if mode not in ['inc', 'update', 'fix']:
            raise ValueError('invalid mode')
        self.mode = mode

    def start_requests(self):
        self.client = pymongo.MongoClient(self.settings.get('MONGO_URI'))
        self.db = self.client[self.settings.get('MONGO_DATABASE')]
        tvs = self.db['TVShow']
        stvs = tvs.find().sort('play_id', -1)
        empty = tvs.count() == 0

        if self.mode == 'inc':
            bPage = self.bPage if empty else (int(stvs[0]['play_id']) + 1)
            start_urls = [BASE_URL.format(bPage)]
        elif self.mode == 'update':
            toUpdate = tvs.find({'status': {'$ne': '完结'}})
            start_urls = [
                BASE_URL.format(t['play_id']) for t in toUpdate
            ]
        elif self.mode == 'fix':
            start_urls = []
            if not empty:
                last = int(stvs[0]['play_id'])
                for i in range(1, last + 1):
                    if not tvs.find_one({'play_id': i}):
                        start_urls.append(BASE_URL.format(i))

        self.client.close()
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """解析"""
        play_id = re.search(r'viewtvplay-(\d+)\.html', response.url).group(1)
        if response.xpath('//div[@id="messagetext"]'):
            # 该剧不存在
            self.errCount += 1
            if self.errCount == self.errLimit:
                self.logger.info('err play id: {}'.format(play_id))
                return
        else:
            yield self.parse_tvshow(play_id, response)
            # 解析资源
            for tr in response.xpath('//tbody[@id="ajax_tbody"]/tr'):
                yield response.follow(
                    tr.xpath('./td[2]/a')[0],
                    callback=self.parse_resource,
                    meta={
                        'play_id': play_id,
                        'download_count': tr.xpath('./td[4]/text()').extract_first()
                    })
        if self.mode == 'inc':
            yield response.follow(
                BASE_URL.format(int(play_id) + 1), callback=self.parse)

    def parse_resource(self, response):
        """解析资源"""
        l = MyLoader(item=Resource(), response=response)
        l.add_value('play_id', response.meta['play_id'])
        l.add_value('download_count', response.meta['download_count'])
        l.add_xpath('name', '//span[@id="pdtname"]/text()')
        l.add_xpath('size', '//span[@class="fmb f2"]', re=r'\[(.*?)\]')
        l.add_xpath('ed2k', '//dd[@id="emule_url"]')
        l.add_xpath('magnet', '//dd[@id="torrent_url"]')
        return l.load_item()

    def parse_tvshow(self, play_id, response):
        """解析电视剧信息"""
        xpath = '//ul[@class="detail-inf-list"]'
        p = r'<li><strong>{}：<\/strong>(.*?)<\/li>'

        l = MyLoader(item=TVShow(), response=response)
        l.add_value('play_id', play_id)
        l.add_xpath('name', '//span[@id="pdtname"]/text()')
        l.add_xpath('rating', '//b[@class="f1"]/text()')
        l.add_xpath('raters', xpath, re=r'<\/b>分（(\d+)评）<\/div>')
        l.add_xpath('first_play_at', xpath, re=p.format('首播时间'))
        l.add_xpath('status', xpath, re=p.format('播出状态'))
        l.add_xpath('alias', xpath, re=p.format('别　　名'))
        l.add_xpath('typo', xpath, re=p.format('类　　型'))
        l.add_xpath('intro', '//div[@id="shortDesc"]')
        l.add_xpath(
            'img_url',
            '//div[@class="detail-img-pic"]/span/a/attribute::href')

        return l.load_item()
