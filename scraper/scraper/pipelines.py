import app
from app import service_table, brands_table, session, Products
from scrapy.exceptions import DropItem
from time import localtime, strftime
import logging
logging.basicConfig()

class ScraperPipeline():

	def __init__(self):
		self.st = service_table
		self.bt = brands_table
		self.session = session
		self.Products = Products

	def process_item(self, item, spider):

		allowed_brands = self.bt[spider.name].tolist()
		allowed_sale = float(self.st[spider.name].tolist()[2])
	

		if item["brand"].lower() in allowed_brands and item["sale"] >= allowed_sale:

			try:
				item_stored = self.session.query(self.Products).filter(self.Products.product_id.like("%{}%".format(item["product_id"]))).first()

				# Data Base Update scenario
				if item["new_price"] != item_stored.new_price:
					
					item_stored.new_price = item["new_price"]
					item_stored.new_price = item["old_price"]
					item_stored.last_updated = strftime("%Y-%m-%d", localtime())

					self.session.commit()

					return item

				else:  				
					raise DropItem("Item's price hasn't changed!")	

			# Append to Data Base scenario		
			except AttributeError:

				last_item_stored = self.session.query(self.Products).order_by(self.Products.id.desc()).first().product_id
				next_item_counter = int(last_item_stored.split("-")[0]) + 1

				new_item = self.Products(
					product_id = "{}-{}".format(next_item_counter, item["product_id"]),
					title = item["titles"],
					new_price = item["new_price"],
					old_price = item["old_price"],
					product_url = item["product_url"],
					img_hash = item["img_hash"],
					stars = item["stars"],
					comments = item["comments"],
					sale = item["sale"],
					date_added = strftime("%Y-%m-%d", localtime()),
					spider = spider.name, 
					brand = item["brand"]
					)


				self.session.add(new_item)
				self.session.commit()
				
				return item
	
		else: 
			raise DropItem("Price or Sale criteria was not met!")
