# import the necessary packages
from PttImageSpider.items import PttImage
import scrapy
 
class PttSpider(scrapy.Spider):
       name = "ptt-spider"
       start_urls = ["https://www.ptt.cc/bbs/NounenRena/index.html"]     
       #start_urls = ["https://www.ptt.cc/bbs/Beauty/index.html"] 
       #start_urls = ["https://www.ptt.cc/bbs/akb48/index.html"]       

       def parse(self, response):          
          for href in response.xpath('//div[@class="title"]/a/@href'):
              href_url = 'https://www.ptt.cc' + href.extract()
              print href_url
              yield scrapy.Request(href_url, self.parse_images)
                   
          previouspage = response.xpath('//a[@class="btn wide"]/@href')[1]
          previouspage = 'https://www.ptt.cc' + previouspage.extract()         
          yield scrapy.Request(previouspage, self.parse)


       def parse_images(self, response):        
         for img in response.xpath('//img/@src'):
            if img.extract().find("http") == -1 :
               imageURL = "http:" + img.extract()
            else :
               imageURL = img.extract()
            yield PttImage( file_urls=[imageURL] )
	 






