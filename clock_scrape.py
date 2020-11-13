from scraper.scraper.spiders.iherb_spider import IherbSpider
from scraper.scraper.spiders.apple_spider import AppleSpider
from scraper.scraper.spiders.ozon_spider import OzonSpider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import scrapy
import os
import schedule
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import update, or_
from botocore.exceptions import ClientError
from app.post_generator import PostGenerator, Notifier
from app import s3, rds, session, bucket, Products
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from time import localtime, strftime
from random import shuffle
import collections
import numpy as np
import pandas as pd 




settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'scraper.scraper.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')


def harvest_all():
    process = CrawlerProcess(settings)
    process.crawl(IherbSpider)
    process.crawl(AppleSpider)
    process.crawl(OzonSpider)
    process.start()

def read_image_from_s3(folder, filename):	

	obj_origin = bucket.Object(folder + filename)
	response = obj_origin.get()
	file_stream = response["Body"]
	
	return file_stream

def send_products():    

	current_date = strftime("%Y-%m-%d", localtime())

	latest_products = session.query(Products).filter(or_(
	Products.date_added == current_date,
	Products.last_updated == current_date)).all()

	shuffle(latest_products)

	sleep_sec = (12 * 3600 / int(len(latest_products)))

	ntf_start = Notifier(items=latest_products)
	ntf_start.send_item_count(sleep_sec)


	for product in latest_products:

		if rds.get(product.product_id) is None or product.last_updated == current_date:

			try:
				with Image.open(read_image_from_s3(os.environ.get("S3_IMAGE_FOLDER"), product.img_hash)) as img:

					sale = "-{}%".format(round(product.sale * 100), 1)
					template = Image.open(read_image_from_s3("", os.environ.get("S3_TEMPLATE")))
					cloud_font = os.environ.get("S3_TEMPLATE_FONT")

					try:
						font = ImageFont.truetype(cloud_font, 100)
					except OSError:
						bucket.download_file(Key=cloud_font, Filename=cloud_font)
						font = ImageFont.truetype(cloud_font, 100)
				
					draw = ImageDraw.Draw(template)
					draw.text((23,94), text=sale, font=font, fill="white")	

					if img.size != (1084, 736):

						bg_color = img.getpixel((0, 0))
						base_im = Image.new("RGBA", (1084,736), color=bg_color)
						maxsize = (800, 650)
						img.thumbnail(maxsize, Image.ANTIALIAS)
						img_w, img_h = img.size
						bg_w, bg_h = base_im.size
						offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
						base_im.paste(img, offset)
						img_png = base_im.convert("RGBA")
						img_png.paste(template, (600, 100), mask=template)
						
						pg = PostGenerator(product, img_png)
						pg.send_product()

					else:
						
						img_png = img.convert("RGBA")
						img_png.paste(template, (600, 100), mask=template)

						pg = PostGenerator(product, img_png)
						pg.send_product()	

					# Recording PID as posted into redis
					rds.set(product.product_id, str(product.date_added))
					time.sleep(sleep_sec)

			except ClientError as ex:
				if ex.response["Error"]["Code"] == "NoSuchKey":	

					session.query(Products).filter(Products.product_id == product.product_id).delete()
					session.commit()		
	
		else:
			continue

	ntf_end = Notifier(text="No items left for posting")
	ntf_end.send_items_ended()	




schedule.every().day.at("08:00").do(harvest_all)
schedule.every().day.at("09:00").do(send_products)

while True:
	schedule.run_pending()
	time.sleep(1)

