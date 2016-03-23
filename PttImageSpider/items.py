# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PttimagespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PttImage(scrapy.Item):
      title = scrapy.Field()
      image_urls = scrapy.Field()
      images = scrapy.Field()

