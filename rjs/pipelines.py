# -*- coding: utf-8 -*-
import re
from datetime import datetime

import pymongo
from scrapy.exceptions import DropItem

from rjs.items import TVShow, Resource, TypoRelation, ActorRelation


class MongoPipeline:
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def save(self, item, query=None):
        if query:
            self.db[item.__class__.__name__].update_one(
                query,
                {'$set': item},
                upsert=True
            )
        else:
            self.db[item.__class__.__name__].insert_one(dict(item))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, TVShow):
            return self.process_tvshow(item)
        elif isinstance(item, Resource):
            return self.process_resource(item)
        else:
            raise DropItem('Invalid item {}'.format(item))

    def process_resource(self, item):
        item['download_count'] = int(item['download_count'])
        self.save(item, {'play_id': item['play_id'], 'name': item['name']})
        return item

    @staticmethod
    def hopeMatch(match, idx):
        if not match:
            return ''
        try:
            return match.group(idx)
        except IndexError:
            return ''

    def process_tvshow(self, item):
        if item.get('name'):
            item['play_id'] = int(item['play_id'])
            name_match = re.search(r'《(.*?)》.*?\((.*?)\)', item['name'])
            item['name_cn'] = self.hopeMatch(name_match, 1)
            item['name_en'] = self.hopeMatch(name_match, 2)
            if item.get('first_play_at'):
                date_match = re.search(
                    r'^(\d+-\d+-\d+) / (.*?)$',
                    item['first_play_at'])
                item['first_play_date'] = self.hopeMatch(date_match, 1)
                item['season'] = self.hopeMatch(date_match, 2)
            item['last_updated'] = datetime.now().timestamp()
            item['intro'] = item.get('intro', '').replace('\r\n', '\n')
            item['typo'] = item.get('typo', '')
            item['alias'] = item.get('alias', '')
            # 存储关联表
            for t in item['typo'].split('/'):
                self.save(TypoRelation(typo=t, play_id=item['play_id']))
            for a in item['alias'].split('/'):
                self.save(ActorRelation(actor=a, play_id=item['play_id']))
            self.save(item, {'play_id': item['play_id']})
            return item
        else:
            raise DropItem('Missing name in {}'.format(item))
