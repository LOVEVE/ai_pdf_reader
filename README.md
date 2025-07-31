# AI PDF 閱讀器

這個專案實現了一個簡單的網頁應用程式，用於上傳 PDF、解析內容並通過 DeepSeek API 進行問答。功能類似於 ChatPDF，但完全在本地運行。前端採用簡單的 HTML/JavaScript，後端使用 Flask。

## 特色

* **PDF 上傳與解析**：使用 PyPDF2 將使用者上傳的 PDF 一項項解析為純文字。
* **問答介面**：解析完成後，使用者可以輸入問題，後端會將問題與 PDF 內容一併傳送至 DeepSeek 模型，取得回答並顯示於介面中。
* **與 DeepSeek API 相容**：DeepSeek API 的呼叫格式與 OpenAI 相容【125360099820378†screenshot】。只需在 `.env` 或環境變數中設定 `DEEPSEEK_API_KEY` 即可。
* **Docker 化部署**：提供 `Dockerfile`，可直接建置映像並以容器方式執行。

## 安裝與執行

1. 下載或複製此專案至本地：

   ```bash
   git clone <your-repo-url>
   cd ai_pdf_reader
   ```

2. 建立並啟動虛擬環境（選用）：

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. 安裝依賴：

   ```bash
   pip install -r requirements.txt
   ```

4. 設定 DeepSeek API 金鑰：

   向 DeepSeek 申請 API 金鑰，並在環境變數中設定：

   ```bash
   export DEEPSEEK_API_KEY=sk-...  # 將 ... 替換為您的金鑰
   ```

5. 啟動應用程式：

   ```bash
   python app.py
   ```

6. 在瀏覽器中開啟 `http://localhost:5000`，即可上傳 PDF 並開始提問。

### 使用 Docker

若偏好使用容器，可直接建立並執行 Docker 映像：

```bash
# 在專案根目錄執行
docker build -t ai-pdf-reader .
docker run --rm -p 5000:5000 -e DEEPSEEK_API_KEY=sk-... ai-pdf-reader
```

然後開啟 `http://localhost:5000` 即可。請確保用環境變數傳入有效的 `DEEPSEEK_API_KEY`。

## 深入說明

### DeepSeek API

DeepSeek 提供的 Chat Completion 端點與 OpenAI API 的格式一致，只需改變 base URL 和金鑰【125360099820378†screenshot】。官方文件中的範例指出，`https://api.deepseek.com/chat/completions` 端點接受類似以下的 JSON 請求【80667180641075†screenshot】：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"}
  ],
  "stream": false
}
```

本應用在提問時會使用解析出的 PDF 文字作為系統提示的一部分，以使模型回答與文件內容相關的答案。使用者的問題則以 `user` 角色傳送。

### 重要注意事項

* 為了簡化範例，本程式將上傳的 PDF 內容和聊天歷史保存在全域變數中，並未實作使用者區分或持久化。如果要在多用戶或生產環境使用，請自行增加身份識別與資料庫支援。
* DeepSeek API 有請求速率和價格限制，詳情請參考官方文件。
* 大型 PDF 可能超出模型的上下文限制，程式會自動截斷前 8000 個字元傳給模型。根據實際需要可調整。

## 授權

本專案採用 MIT 授權，詳見專案根目錄之 `LICENSE` 檔案（如有）。
