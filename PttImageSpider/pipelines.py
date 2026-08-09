# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


class PttImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            # 對 imgur 圖片特殊處理，避免 403 錯誤
            if 'imgur.com' in image_url:
                # 偽裝 Referer 為 imgur 自己
                yield scrapy.Request(image_url, meta={'item': item},
                                   headers={'Referer': 'https://imgur.com/'})
            else:
                yield scrapy.Request(image_url, meta={'item': item})
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        if item is None:
            item = request.meta.get('item', {})
        #取得網址最後一個字串做為檔名
        name = request.url.split('/')[-1]
        filename = '{0[title]}/{1}'.format(item, name)
        return filename
    
