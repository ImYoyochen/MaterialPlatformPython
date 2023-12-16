# MaterialPlatformPython

本地執行時創建虛擬環境（可選但建議）。
```
python -m venv env
```
啟動環境
```
.\env\Scripts\activate
```
安裝依賴項
```
pip install -r requirements.txt
```
啟動應用程序
```
python .\ImpactCalculator1.py
```

包版上GCP時
```
記得於.gcloudignore排除env資料夾
```
執行GCP CLI包版
```
gcloud app deploy app.yaml
