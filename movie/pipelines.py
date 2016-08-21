# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MoviePipeline(object):
    def process_item(self, item, spider):
        return item

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
           yield scrapy.Request(image_url)
