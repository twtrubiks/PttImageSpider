# PTT 爬蟲圖片下載器 (使用Scrapy) PttImageSpider

抓取PTT整個看板的圖片，並用文章標題作為資料夾的名稱

* [Demo Video](https://www.youtube.com/watch?v=B78ZYEjkSaY) - Linux V2 (demo )
* [Demo Video](https://youtu.be/6BHiLOtsW2Y) - Linux V1 (教學+demo )

## 特色

* 抓取PTT特定看板全部的圖片
* 使用文章標題作為資料夾的名稱
* 下載圖片速度非常快，1分鐘可抓600張圖片，平均每秒10張

## 使用方法

```cmd
scrapy crawl ptt_img_spider
```

如需抓其他PTT的看板，需要修改路徑 PttImageSpider/PttImageSpider/spiders/pttspider.py 檔案裡的

```python
start_urls = ["https://www.ptt.cc/bbs/AKB48/index.html"]
```

將網址修改為其他看板的網址，範例如下

```python
start_urls = ["https://www.ptt.cc/bbs/NounenRena/index.html"]
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

* Python 3.12+
* Scrapy 2.13.3
* Pillow 10.0+
* brotli 1.0+ (用於解壓縮 PTT 網頁內容)

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

### 爬蟲速度優化

專案使用了以下設定來平衡爬取速度與伺服器負載：

- `DOWNLOAD_DELAY = 0.5` - 請求間隔 0.5 秒

- `CONCURRENT_REQUESTS = 8` - 並發請求數

- `AUTOTHROTTLE_ENABLED = True` - 自動調節速度

## License

MIT license
