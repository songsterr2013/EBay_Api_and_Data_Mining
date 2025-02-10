# eBay電商平台上爵士音樂家唱片的商品分析
## 專案摘要:
### 「一鍵搜尋並匯出 eBay 當下的商品資訊，專為爵士樂黑膠唱片收藏者設計的高效工具。」
* 使用者僅需輸入爵士音樂家名稱如'Bill Evans'，將自動從eBay上收集該藝人所有黑膠唱片的商品資訊
* 資料將經過自動化整理，匯出一份excel data供檢閱
* 最後自動生成Tableau儀表板，透過圖表來呈現相關的唱片資訊
* 能夠迅速掌握該位藝人的「人氣專輯排名」、「最有收藏價值的唱片排名」等資訊

## 動機:
### 「此項目的目的是為了解決用戶在尋找爵士音樂黑膠唱片時耗時較長的問題。從而設計一個工具，透過自動化的方式快速抓取 eBay 商品數據並整理成有用的資料格式。」
* 近3-5年，黑膠唱片掀起一股復興潮，爵士樂在黑膠唱片成為主要的音樂錄製媒介中扮演重要的角色
* 爵士二手黑膠在市場上極具收藏價值，因其原始錄音的稀有性，價格只會變得愈來愈貴
* 身為爵士二手黑膠的收藏者，總是希望能買到稀有的版本，但礙於平台上的資訊繁複和搜索的不便性，總需花費大量時間「挖寶」
* 因此該專案的目的旨在減少一切重複且耗時的資訊挖掘過程，將資料整理成易於解讀的圖表形式來呈現
* 從而協助使用者去了解「真正有收藏價值的」爵士二手黑膠，在購買階段中能做出更有利的選擇

## 各檔案的基本說明:
* Ebay.py -> 可獨立運行的模組1，負責call eBay api，並將data匯出為xlsx檔到指定路徑
* DataCleaning.py -> 可獨立運行的模組2，負責處理多份xlsx檔，合併、整理欄位和進行基本資料清洗，並匯出到指定路徑
* CreateTableau.py -> 可獨立運行的模組3，負責將Tableau模板的twb檔複製到指定路徑
* main.py -> 整合器，使上面3支py檔依次執行並重複
* util.py -> 工具模組，負責日志管理、json讀寫和資料夾創建等工作
* config.json -> 存放call eBay api的關鍵字，主要是模組1, 2, 3各自都依賴其"keywords"，以及模組1在資料處理過程中所依賴的相關欄位名稱
* Discography -> 裡面都是xlsx檔，目前存放了30位爵士巨頭的專輯資訊，檔案皆經過特別的處理，使得程式能順利進行匹配
* eBay電商平台上的唱片商品分析(模板) -> Tableau模板，負責複製用

## 相關套件:
* pandas~=2.2.3
* python-dotenv~=1.0.1
* ebaysdk~=2.2.0
* tqdm~=4.67.1

## 使用方法:
1. 確保 requirements 中的套件已安裝好，以及確保上方共8個檔案和資料夾放在同一路徑中
2. 準備好你的ebay api key，在eBay Developers Program中申請，在同一路徑中創建.env，放入你的API_KEY
3. 有3種方法可以輸入搜尋關鍵字:
   * 方法1: 輸入關鍵字 (單次搜索)
   * 方法2: 讀json檔 (把多個藝人寫到config.json中的"jazz_giant"裡)
   * 方法3: 直接在 main.py 中修改jazz_giant列表 (由於開發初期，目前用的是方法3)
4. 假設已設定好jazz_giant =['Bill Evans']，並直接執行main.py
5. 同一路徑中會生成名為'data'的資料夾，裡面也會生成名為'data_Bill_Evans'的資料夾，裡面將包含從api中取得的raw data和'Bill_Evans_data'，以及'eBay電商平台上的Bill Evans唱片商品分析.twb'
6. 關於'eBay電商平台上的Bill Evans唱片商品分析.twb'的使用需要有Tableau的基本操作知識，將資料來源更改為'Bill_Evans_data'即可正常呈現儀表板
7. Ebay.py 負責 生成raw data，而DataCleaning.py則負責將所有開頭名為'ebay_data'的xlsx合併並進行處理
8. 如想控制raw data資料生成，在config.json中修改"entry_per_page"和"max_pages"
9. 目前正計劃在每日5000次api的限制下，控制"entry_per_page"和"max_pages"，以減少重複的data獲取，但需基於平台商品更新速度來制定次數
10. 後續如果想分析你所感興趣的任何藝人，自行去修改jazz_giant，同時新增屬於他的discography，如單純只需要raw data則可略過discography創建
11. 如果想進行所有藝人的分析，util.py中的combine_excel_files可將'data'所有藝人資料夾中的'_data'合併，然後使用Tableau或其他分析工具
