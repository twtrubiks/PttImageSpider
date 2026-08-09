# PTT 爬蟲圖片下載器 (使用Scrapy) PttImageSpider

抓取PTT整個看板的圖片，並用文章標題作為資料夾的名稱

* [Demo Video](https://www.youtube.com/watch?v=B78ZYEjkSaY) - Linux V2 (demo )
* [Demo Video](https://youtu.be/6BHiLOtsW2Y) - Linux V1 (教學+demo )

## 特色

* 抓取PTT特定看板全部的圖片
* 使用文章標題作為資料夾的名稱
* 可指定看板，也可只抓特定作者的文章
* 預設刻意降速以減輕站台負擔，實測約每分鐘 100 張圖片，可用參數解除限制（詳見技術說明）

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

## 抓取範圍

預設沒有數量限制，會從看板最新的一頁開始，一路往回抓到最舊的第一頁。

抓取順序是由新到舊。想「只抓最近的圖」不需要改程式，跑一陣子按 Ctrl + C 中斷即可。

這個順序需要 `settings.py` 裡的 `DEPTH_PRIORITY` 與兩個 FIFO 佇列設定才成立，詳見下方技術說明的「廣度優先走訪」。

Scrapy 預設的 LIFO 佇列會讓同一頁的文章由下往上處理，最新的幾篇反而最後才抓。

實際下載完成的順序仍然不會完全照這個排列，因為同時會有多個下載在進行，誰先傳完誰先寫入。

**關於中斷：**

按第一次 Ctrl + C 時 Scrapy 會優雅收尾，把已經在進行中的下載處理完再關閉，並輸出統計資訊。

收尾可能要等數十秒。不想等的話再按第二次 Ctrl + C 會立即強制中斷，但可能留下寫到一半的圖片檔。

也可以用參數限制範圍，不必手動中斷：

```cmd
scrapy crawl ptt_img_spider -s CLOSESPIDER_ITEMCOUNT=50
scrapy crawl ptt_img_spider -s CLOSESPIDER_TIMEOUT=300
```

這兩個都是 Scrapy 內建的設定，用 `-s` 指定只影響這次執行，不會改到 settings.py。

`CLOSESPIDER_ITEMCOUNT` 是抓到幾篇就停。算的是「成功存到圖的文章數」。

`CLOSESPIDER_TIMEOUT` 是跑幾秒就停，單位是秒，從爬蟲啟動開始計時。

兩者觸發時都是優雅關閉，會先把進行中的下載處理完，所以實際的篇數和時間都會比設定值再多一些。

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

### 廣度優先走訪

爬蟲走訪的結構是一棵樹：一頁列表底下掛著該頁的每篇文章，以及下一頁的列表。

```
列表第 1 頁
├── 文章 1 ~ 文章 20
└── 列表第 2 頁
    ├── 文章 21 ~ 文章 40
    └── 列表第 3 頁 ...
```

Scrapy 預設是深度優先，解析完一頁後會立刻往下一頁列表衝，該頁的文章先擱在佇列裡。

廣度優先則是把當前這一頁的文章全部抓完，才前往下一頁，也就是「先把這一層看完再往下一層」。

`settings.py` 用三個設定達成這件事：

- `DEPTH_PRIORITY = 1` - 越淺的請求優先權越高，決定層與層之間的順序

- `SCHEDULER_MEMORY_QUEUE` - 改成 FIFO，同一層照放入的順序處理，也就是列表頁由上到下（新到舊）

- `SCHEDULER_DISK_QUEUE` - 同一件事的磁碟版本，設了 `JOBDIR` 續爬時才會用到

兩種走訪方式的下載速率實測幾乎相同，差別只在力氣花在哪：深度優先快速往回翻頁，廣度優先把當前頁抓完整。

### 爬取速度與限速機制

專案預設是刻意降速的，用以下設定平衡爬取速度與伺服器負載：

- `DOWNLOAD_DELAY = 0.5` - 同一網域的請求間隔 0.5 秒

- `CONCURRENT_REQUESTS = 8` - 全域並發請求數

- `CONCURRENT_REQUESTS_PER_DOMAIN = 4` - 單一網域並發請求數

- `AUTOTHROTTLE_ENABLED = True` - 依回應延遲自動調節速度

**想跑更快：**

用 `-s` 覆寫設定即可，不需要修改 settings.py：

```cmd
scrapy crawl ptt_img_spider -s DOWNLOAD_DELAY=0 -s AUTOTHROTTLE_ENABLED=False -s CONCURRENT_REQUESTS_PER_DOMAIN=16
```

同樣條件下實測可到每分鐘約 980 張（每秒 16 張），全程沒有被對方站台限流。

但這等於放棄了禮貌降速，請自行斟酌對方站台的負擔。

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
