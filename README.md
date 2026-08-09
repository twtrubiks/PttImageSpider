# PTT 爬蟲圖片下載器 (使用Scrapy) PttImageSpider

抓取PTT整個看板的圖片，並用文章標題作為資料夾的名稱

* [Demo Video](https://www.youtube.com/watch?v=B78ZYEjkSaY) - Linux V2 (demo )
* [Demo Video](https://youtu.be/6BHiLOtsW2Y) - Linux V1 (教學+demo )

## 特色

* 抓取PTT特定看板全部的圖片
* 使用文章標題作為資料夾的名稱
* 可指定看板，也可只抓特定作者的文章
* 下載圖片速度非常快，1分鐘可抓600張圖片，平均每秒10張

## 使用方法

抓取預設看板 (AKB48) 的全部圖片

```cmd
scrapy crawl ptt_img_spider
```

用 `-a board=板名` 指定其他看板，不需要修改程式碼

```cmd
scrapy crawl ptt_img_spider -a board=NounenRena
```

用 `-a author=作者ID` 只抓特定作者的文章，兩個參數可以一起用

```cmd
scrapy crawl ptt_img_spider -a author=emperor
scrapy crawl ptt_img_spider -a board=NounenRena -a author=emperor
```

如果想直接改掉預設看板，修改 PttImageSpider/PttImageSpider/spiders/pttspider.py 裡的

```python
default_board = "AKB48"
```

## 執行畫面

![alt tag](http://i.imgur.com/loYZHTi.jpg)

有些看板的網頁頁數非常多，所以如果要強迫終止，可以按 Ctrl + Z 強制結束程式

## 輸出格式

圖片會儲存在專案根目錄的 `images/` 資料夾下：

```
images/
├── [文章標題1]/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── [文章標題2]/
│   └── ...
└── ...
```

每篇文章的圖片會以文章標題作為資料夾名稱進行分類儲存。

## 執行環境

* Python 3.13
* Scrapy 2.17.0
* Pillow 12.0+
* brotli 1.0+ (用於解壓縮 PTT 網頁內容)

安裝套件

```cmd
pip install -r requirements.txt
```

## 技術說明

### Brotli 壓縮支援

PTT 網站使用 Brotli 壓縮（br encoding）來傳輸網頁內容。Scrapy 的 `HttpCompressionMiddleware` 會自動處理各種壓縮格式：

- **gzip, deflate** - Scrapy 內建支援

- **br (Brotli)** - 需要安裝 brotli 套件

**自動處理機制：**

只要安裝 brotli 套件（`pip install brotli`），Scrapy 會自動：

1. 偵測伺服器回應的 `Content-Encoding: br`

2. 使用 brotli 解壓縮網頁內容

3. 不需要撰寫任何額外程式碼

這是 Scrapy「電池內建」(batteries included) 的設計理念 - 安裝套件即可使用，完全自動化。

### imgur 圖片下載處理

本專案特別處理了 imgur 圖片的下載問題。imgur 會檢查 HTTP Referer header 來防止盜連（Hotlinking），

當偵測到請求來自 PTT 時會返回 403 Forbidden 錯誤。

**解決方案：**

在 `pipelines.py` 中，對 imgur 圖片請求特別處理，將 Referer 偽裝為來自 imgur 自己的網站：

```python
def get_media_requests(self, item, info):
    for image_url in item['image_urls']:
        if 'imgur.com' in image_url:
            # 偽裝 Referer 為 imgur 自己，避免 403 錯誤
            yield scrapy.Request(image_url, meta={'item': item},
                               headers={'Referer': 'https://imgur.com/'})
        else:
            yield scrapy.Request(image_url, meta={'item': item})
```

**Referer 原理：**

- Referer 是 HTTP 請求頭，告訴伺服器請求的來源頁面

- imgur 使用此機制防止其他網站直接引用圖片

- 透過修改 Referer，讓 imgur 認為請求來自內部，即可正常下載

### 作者過濾的實作方式

指定 `-a author=` 時，並不是把整個看板翻過一遍再逐篇比對作者，而是改用 PTT 的站內搜尋：

```
https://www.ptt.cc/bbs/AKB48/search?q=author%3Aemperor
```

搜尋結果頁的 HTML 結構與看板列表頁完全相同（同樣的 `div.r-ent` 與 `a.btn wide` 分頁按鈕），

所以 `parse()` 不需要任何修改就能直接沿用，只有 `start_urls` 不一樣。

**為什麼不用逐篇過濾：**

看板列表可能有幾千頁，逐篇過濾還是得從頭走到尾，只省下載圖片的時間。

改用站內搜尋則只會走訪確實有該作者文章的頁面，冷門作者甚至只有一頁，差距非常大。

### 圖片方向自動校正

從 Scrapy 2.14 起，`ImagesPipeline` 會依照圖片的 EXIF 資訊自動轉正（transpose）方向，

手機拍攝後上傳的橫躺圖片下載後會是正確的方向，不需額外處理。

### 爬蟲速度優化

專案使用了以下設定來平衡爬取速度與伺服器負載：

- `DOWNLOAD_DELAY = 0.5` - 請求間隔 0.5 秒

- `CONCURRENT_REQUESTS = 8` - 並發請求數

- `AUTOTHROTTLE_ENABLED = True` - 自動調節速度

## License

MIT license

## Donation

文章都是我自己研究內化後原創，如果有幫助到您，也想鼓勵我的話，歡迎請我喝一杯咖啡 :laughing:

綠界科技ECPAY ( 不需註冊會員 )

![alt tag](https://payment.ecpay.com.tw/Upload/QRCode/201906/QRCode_672351b8-5ab3-42dd-9c7c-c24c3e6a10a0.png)

[贊助者付款](http://bit.ly/2F7Jrha)

歐付寶 ( 需註冊會員 )

![alt tag](https://i.imgur.com/LRct9xa.png)

[贊助者付款](https://payment.opay.tw/Broadcaster/Donate/9E47FDEF85ABE383A0F5FC6A218606F8)

## 贊助名單

[贊助名單](https://github.com/twtrubiks/Thank-you-for-donate)
