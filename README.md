# PTT 爬蟲圖片下載器 (使用Scrapy) PttImageSpider
抓取PTT整個看板的圖片，並用文章標題作為資料夾的名稱 
* [Demo Video](https://www.youtube.com/watch?v=B78ZYEjkSaY) - Linux V2 (demo )
* [Demo Video](https://youtu.be/6BHiLOtsW2Y) - Linux V1 (教學+demo )

## 特色
* 抓取PTT特定看板全部的圖片
* 使用文章標題作為資料夾的名稱 
* 下載圖片速度非常快，1分鐘可抓600張圖片，平均每秒10張

## 使用方法
```
scrapy crawl ptt_img_spider
```
如需抓其他PTT的看板，需要修改路徑 PttImageSpider/PttImageSpider/spiders/pttspider.py 檔案裡的 <br>
```
start_urls = ["https://www.ptt.cc/bbs/AKB48/index.html"]
```
將網址修改為其他看板的網址，範例如下<br>
```
start_urls = ["https://www.ptt.cc/bbs/NounenRena/index.html"]   
```

## 執行畫面
![alt tag](http://i.imgur.com/loYZHTi.jpg)<br>
有些看板的網頁頁數非常多，所以如果要強迫終止，可以按 Ctrl + Z 強制結束程式 <br>

## 輸出格式
![alt tag](http://i.imgur.com/Uc6tDcr.jpg)
![alt tag](http://i.imgur.com/CFiUo7E.jpg)

## 執行環境
* Ubuntu 12.04
* Python 2.7.3
* Scrapy 1.0.4

## License
MIT license

