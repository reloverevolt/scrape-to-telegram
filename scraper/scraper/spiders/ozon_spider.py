#-*- coding: utf-8 -*-
import scrapy
from ..items import ScraperItem
import re
import hashlib
import json

class OzonSpider(scrapy.Spider):
	name = 'ozon-spider'
	allowed_domains = ['www.ozon.ru']

	def start_requests(self):

		for i in range(30):
			yield scrapy.Request("https://www.ozon.ru/highlight/45029/?isdiscount=t&rating=t&page={}".format(i), self.parse)
            
	def parse(self, response):

		data = response.css("div#state-searchResultsV2-312617-default-1::attr(data-state)").get()
		data_json = json.loads(data)

		items = ScraperItem()

		for unit in data_json["items"]: 

			items["titles"] = unit["cellTrackingInfo"]["title"]
			items["brand"] = unit["cellTrackingInfo"]["brand"]

			old_price = unit["cellTrackingInfo"]["price"]
			items["old_price"] = old_price

			new_price = unit["cellTrackingInfo"]["finalPrice"]
			items["new_price"] = new_price
		
			items["product_id"] = "OZ" + str(unit["cellTrackingInfo"]["id"])
			items["stars"] = round(unit["cellTrackingInfo"]["rating"], 2)
		
			image_urls = unit["images"][0]
			items["image_urls"] = [image_urls]

			items["product_url"] = "https://www.ozon.ru" + unit["link"].split("?")[0]
			items["sale"] = round((old_price - new_price) / old_price, 3)

			try:
				items["comments"] = unit["templateState"][1]["components"][3]["commentsCount"]
			except KeyError:
				items["comments"] = 0

			items["img_hash"] = "{}.jpg".format(hashlib.sha1(image_urls.encode()).hexdigest())

			yield items


        