# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


class MyLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags)
    default_output_processor = TakeFirst()
