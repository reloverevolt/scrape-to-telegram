import scrapy
from .. items import ScraperItem
import hashlib
import re


class IherbSpider(scrapy.Spider):
	name = 'iherb-spider'
	allowed_domains = ["ru.iherb.com"]


	def start_requests(self):

		for i in range(31):
			yield scrapy.Request("https://ru.iherb.com/specials?p={}".format(i), self.parse)

	def parse(self, response):

		for product in response.xpath("//div[contains(@class, 'product-cell-container')]"):

			items = ScraperItem()

			# Titles Extraction 

			titles = product.xpath(".//div[@class='absolute-link-wrapper']//a/@title").get().replace("\xa0", " ")

			items["titles"] = titles
			items["brand"] = titles.split(",")[0]
			
			# Prices Extraction - Not Unified

			pr = product.xpath(".//span[contains(@class, 'price')]//bdi/text()").getall()

			if len(pr) == 2:

				new_price = float(pr[0].replace("₽", "").replace(",", ""))
				old_price = float(pr[1].replace("₽", "").replace(",", ""))
				items["new_price"] = new_price
				items["old_price"] = old_price

			else:

				continue	


			# Product ID Extraction	
			
			items["product_id"] = "IH"+ str(product.xpath(".//div[@style='display:none']//input/@value").get())		


			# Product URLs Extraction

			items["product_url"] = product.xpath(".//div[@class='absolute-link-wrapper']//a/@href").get()


			# Image URLs Extraction 

			image_urls = product.xpath(".//div[@class='product-image-wrapper']").re(r"https.+\/u\/[0-9]+\.jpg")[0].split(" ")[0].replace('"', '')
			
			items["image_urls"] = [image_urls]

			# Stars + Comments Extraction

			try:

				stars = product.xpath(".//div[@class='rating']//a[@class='stars']/@title").re(r".+/")[0].strip("'[]/")

				if "." in stars:

					items["stars"] = float(stars)

				else:

					items["stars"] = int(stars)	

				items["comments"] = int(product.xpath(".//div[@class='rating']//a[@class='stars']/@title").re(r"\s\d+\s")[0])

			except IndexError:

				items["stars"] = 0

				items["comments"] = 0

			
			# Hashing Image Urls

			items["img_hash"] = "{}.jpg".format(hashlib.sha1(image_urls.encode()).hexdigest())

			items["sale"] = round((old_price - new_price) / old_price, 3)

			
			yield items
