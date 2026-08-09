from PttImageSpider.items import PttImage
from urllib.parse import quote
import scrapy

domain = "https://www.ptt.cc"
#預設板名 (可自行修改，或執行時用 -a board=板名 指定)
default_board = "AKB48"

#符合圖片格式的網址
def isImageFormat(link):
    if(link.find('.jpg') > -1 or link.find('.png') > -1 or link.find('.gif') > -1 or link.find('.jpeg') > -1):
       return True;
    return False;

#移除特殊字元（移除Linux上無法作為資料夾的字元）
def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value.rstrip();

class PttSpider(scrapy.Spider):
      name = "ptt_img_spider"
      # -a board=板名     指定看板
      # -a author=作者ID  只抓該作者的文章
      def __init__(self, board=default_board, author=None, *args, **kwargs):
          super().__init__(*args, **kwargs)
          base = f"{domain}/bbs/{board}/"
          if author:
             #用站內搜尋只走訪該作者的文章列表，不必翻完整個看板
             self.start_urls = [base + "search?q=" + quote(f"author:{author}")]
          else:
             self.start_urls = [base + "index.html"]

      def parse(self, response):
         #每篇文章的 標題 網址
         for href in response.xpath('//div[@class="title"]/a'):
             href_url =  domain + href.xpath('@href')[0].extract()
             title =  href.xpath('text()')[0].extract()
             item = PttImage()
             item['title'] = remove(title, r"\/:*?'<>.;&!|`{}")
             #將 item 的值傳過去因為再來要使用 標題 作為資料夾的名稱
             yield scrapy.Request(href_url, callback = self.parse_images, meta={'item': item})           
         #抓取上(下)一頁的 URL
         previouspage = response.xpath('//a[@class="btn wide"]/@href')[1]
         previouspage =  domain + previouspage.extract()         
         yield scrapy.Request(previouspage, self.parse)


      def parse_images(self, response):  
        item = response.meta['item']
        imgurls = []
        #取得每篇文章內的 圖片
        for img in response.xpath('//a/@href'):
            url = img.extract()
            if(isImageFormat(url)):
               imgurls.append(url)
        item['image_urls'] = imgurls
        return  item
	 
       





