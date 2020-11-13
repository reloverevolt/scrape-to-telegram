# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
	
	titles = scrapy.Field()
	new_price = scrapy.Field()
	old_price = scrapy.Field()
	product_id = scrapy.Field()
	product_url = scrapy.Field()
	image_urls = scrapy.Field()
	stars = scrapy.Field()
	comments = scrapy.Field()
	img_hash = scrapy.Field()
	sale = scrapy.Field()
	brand = scrapy.Field()
