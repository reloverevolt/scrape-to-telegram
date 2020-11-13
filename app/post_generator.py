from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app import bot, service_table
import requests
import json
import telegram
import hashlib
import collections
from io import BytesIO
import os

class PostGenerator:

	def __init__(self, product, image_object):
		self.product = product
		self.pid = self.product.product_id
		self.purl = self.product.product_url
		self.title = self.product.title
		self.new_price = self.product.new_price
		self.old_price = self.product.old_price
		self.sale = self.product.sale
		self.image_object = image_object
		self.store = service_table[self.product.spider].tolist()[0]
		self.rcode = service_table[self.product.spider].tolist()[1]
		self.link_title, self.link_button = self.generate_links()
		self.link_chat = os.environ.get("LINK_TO_CHAT")
		self.channel = os.environ.get("CHANNEL_ID")
		self.bot = bot
		

	def generate_links(self):
	
		if self.store == "Золотом Яблоке":

			link_assembled = "{}{}".format(self.rcode, self.purl)	
			link_title = "<a href='{}'>{}</a>".format(link_assembled, self.title)

			return link_title, link_assembled

		else:

			link_assembled = "{}{}".format(self.purl, self.rcode)
			link_title = "<a href='{}'>{}</a>".format(link_assembled, self.title)

			return link_title, link_assembled

	def send_product(self):

		caption = "#{} | <strong>На {}</strong>:\n<strong>{}</strong>\nСтарая цена: {} ₽\n<strong>Новая цена: {} ₽</strong>".format(
			self.pid, self.store, self.link_title, int(self.old_price), int(self.new_price))

		photo = BytesIO()
		photo.name = "image.png"
		self.image_object.save(photo, "PNG")
		photo.seek(0)

		kbrd = [[InlineKeyboardButton(text="❤️", callback_data="like 0"),
			InlineKeyboardButton(text="💩", callback_data="shit 0"),
			InlineKeyboardButton(text="Хочу!", url=self.link_button)],
			[InlineKeyboardButton(text="Обсудить", url=self.link_chat)]]


		reply_markup = InlineKeyboardMarkup(kbrd)        

		self.bot.send_photo(chat_id=self.channel, photo=photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)

class Notifier:

	def __init__(self, items=None, text=None):
		self.items = items
		self.text = text
		self.bot = bot
		self.owner_id = os.environ.get("OWNER_ID")

	def send_item_count(self, delay):

		items_list = [item.spider for item in self.items]
		counter = collections.Counter(items_list)
		items_by_spider = counter.most_common()
		items_count = len(items_list)	

		debug_msg = "Total products to post: {}".format(items_count)

		for item in items_by_spider:
			line = "\n{}: {}".format(item[0], item[1])
			debug_msg += line 

		delay_min = round((delay / 60), 2)	
		debug_msg += "\nDelay: {}min".format(delay_min)

		self.bot.send_message(chat_id=self.owner_id, text=debug_msg)

	def send_items_ended(self):
	
		self.bot.send_message(chat_id=self.owner_id, text=self.text)


