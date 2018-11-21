# -*- coding: utf-8 -*-
import scrapy


# 电视剧
class TVShow(scrapy.Item):
    play_id = scrapy.Field()  # 剧ID
    name = scrapy.Field()  # 完整标题
    name_cn = scrapy.Field()  # 中文名
    name_en = scrapy.Field()  # 英文名
    rating = scrapy.Field()  # 评分(满分5分)
    raters = scrapy.Field()  # 参评人数
    first_play_at = scrapy.Field()  # 首播时间
    first_play_date = scrapy.Field()  # 首播日期
    season = scrapy.Field()  # 季度
    status = scrapy.Field()  # 播放状态(是否完结)
    alias = scrapy.Field()  # 别名
    typo = scrapy.Field()  # 类型
    intro = scrapy.Field()  # 简介
    img_url = scrapy.Field()  # 封面地址
    last_updated = scrapy.Field()  # 上一次更新时间


# 资源
class Resource(scrapy.Item):
    play_id = scrapy.Field()  # 剧ID
    name = scrapy.Field()  # 名称
    size = scrapy.Field()  # 容量
    download_count = scrapy.Field()  # 下载量
    ed2k = scrapy.Field()  # 电驴链接
    magnet = scrapy.Field()  # 磁力链接


# 类型
# class Typo(scrapy.Item):
    # name = scrapy.Field()  # 类型名


# 类型关联表
class TypoRelation(scrapy.Item):
    typo = scrapy.Field()  # 类型
    play_id = scrapy.Field()  # 剧ID

# 演员
# class Actor(scrapy.Item):
    # name = scrapy.Field()  # 名称


# 演员关联表
class ActorRelation(scrapy.Item):
    actor = scrapy.Field()  # 演员
    play_id = scrapy.Field()  # 剧ID
