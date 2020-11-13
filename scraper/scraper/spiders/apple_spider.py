# -*- coding: utf-8 -*- 
import scrapy
from scrapy.http.request import Request
from ..items import ScraperItem
import logging
import hashlib

logging.basicConfig(level=logging.INFO)


class AppleSpider(scrapy.Spider):
    name = 'apple-spider' 
    allowed_domains = ['goldapple.ru']

    def start_requests(self):

        for i in range(30):
            yield scrapy.Request("https://goldapple.ru/rasprodazha?p={}".format(i), self.parse)

        for i in range(10):
            yield scrapy.Request("https://goldapple.ru/parfjumerija?product_list_dir=asc&product_list_order=discount&p={}".format(i), self.parse)

        for i in range(10):
            yield scrapy.Request("https://goldapple.ru/podarochnye-nabory?product_list_dir=asc&product_list_order=discount&p={}".format(i), self.parse) 

    def parse(self, response):
        item = ScraperItem()

        logging.info("item object created")

        # GETTING TITLES

        titles = []
        
        title1 = response.xpath("//div[contains(@class, 'product-item-category-title js-clamping')]//span/text()").extract()
        title2 = response.xpath("//strong[@class='product name product-item-name']//a//span[@class='catalog-product-name-span']/text()").extract()
        brand = response.xpath("//strong[@class='product name product-item-name']//a//span[@class='catalog-brand-name-span']/text()").extract()

        for i in zip(brand, title1, title2):
            string = "{}, {}, {}".format(i[0], i[1], i[2])
            titles.append(string)   

        logging.info("titles collected: {}".format(titles)) 

        # GETTING PRICES

        old_price = []
        op = response.xpath("//span[contains(@id, 'old-price')]//span[@class='price']/text()").extract()

        for z in op:
            f = z.replace("\xa0", "")
            f = f.replace("₽", "")
            old_price.append(int(f))

        logging.info("old prices collected:{}".format(old_price))   

        new_price = []  
        np = response.xpath("//span[contains(@id, 'product-price')]//span[@class='price']/text()").extract()
        for z in np:
            f = z.replace("\xa0", "")
            f = f.replace("₽", "")
            new_price.append(int(f))
        
        logging.info("new prices collected: {}".format(new_price))
        # GETTING PRODUCT LINKS 

        product_url = []    
        purl = response.css("div.product-item-info a::attr(href)").extract()
        for z in purl:
            if z in product_url:
                continue
            else:
                product_url.append(z)   

        logging.info("product urls collected:{}".format(product_url))       
        # GETTING PRODUCT IMAGES        
        
        image_urls = response.css("picture.product-item-photo img::attr(data-src)").extract()

        logging.info("product images collected:{}".format(image_urls))

        product_id = response.xpath("//li[contains(@class, 'item product product-item')]/@data-id").extract()

        logging.info("product ids collected: {}".format(product_id))

        img_hashes = []
        for i in image_urls:
            h = hashlib.sha1(i.encode()).hexdigest()
            img_hashes.append("{}.jpg".format(h))

        for itm in zip(titles, old_price, new_price, product_url, image_urls, product_id, img_hashes):

            item["titles"] = itm[0]
            item["old_price"] = itm[1]
            item["new_price"] = itm[2]
            item["product_url"] = itm[3]
            item["image_urls"] = [itm[4]]
            item["product_id"] = "G"+str(itm[5])
            item["stars"] = 0
            item["comments"] = 0
            item["img_hash"] = itm[6]
            item["sale"] = round((itm[1] - itm[2]) / itm[1], 3)
            item["brand"] = itm[0].split(",")[0]

            yield item
        

