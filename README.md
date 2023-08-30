# 爬蟲-合作金庫即時匯率
Grab the real-time exchange rate information of the TCB

#### 01 主程式碼 [爬蟲](Web_Scraping.py)  
#### 02 網頁 [GUI](run_python_with_gui.py)  
#### 03 config [改時間](config.ini)

## Web-Scraping  
### 爬蟲抓取網站資料  
_預設為2023.8.28 10:00:00_  
<pre>
import requests
from bs4 import BeautifulSoup
import pandas
import json
import configparser

print('web scraping start')
url = 'https://www.tcb-bank.com.tw/personal-banking/deposit-exchange/exchange-rate/spot'

session = requests.Session()

response = session.get(url)
cookies = (session.cookies.get_dict())
cookies_str = ';'.join([f"{key}={value}" for key, value in cookies.items()])

soup = BeautifulSoup(response.text, 'html.parser') 
token = soup.find('input',{'name':'__RequestVerificationToken'}).get('value')

# 創建 ConfigParser 對象
config = configparser.ConfigParser()

# 讀取配置文件
config.read('config.ini')

payload = {
        '__RequestVerificationToken': token,
        'date': config.get('Request','date'),
        'time': config.get('Request','time')
    }

header = {
'Accept': 'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding' : 'gzip, deflate, br',
'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
'Connection': 'keep-alive',
'Content-Length': '158',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie': cookies_str ,
'Host': 'www.tcb-bank.com.tw',
'Origin': 'https://www.tcb-bank.com.tw',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest',
'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"Windows"'
}

click_url = 'https://www.tcb-bank.com.tw/api/client/ForeignExchange/GetSpotForeignExchangeSpecific'

response = requests.post(click_url, data = payload, headers= header)

if response.status_code == 200:
    # 解析返回的內容
       soup = BeautifulSoup(response.content, 'html.parser')
    
    # 在這裡進行您的處理
else:
       print( response.status_code )

data = json.loads(response.text)


# 轉換為pandas DataFrame
df = pandas.DataFrame(data['result'])

# 不同的Currency種類
currencies = df['CurrencyName'].unique()

# 創建一個空的DataFrame用於存儲結果
result_dfs = []

# 遍歷每種Currency
for currency in currencies:
    condition_buy = (df['CurrencyName'] == currency) & (df['Type'] == '買入')
    condition_sell = (df['CurrencyName'] == currency) & (df['Type'] == '賣出')
    
    selected_rows_buy = df.loc[condition_buy]
    selected_rows_sell = df.loc[condition_sell]
    
    specific_data_value_prompt_in = selected_rows_buy.iloc[0, selected_rows_buy.columns.get_loc('PromptExchange')]
    specific_data_value_cash_in = selected_rows_buy.iloc[0, selected_rows_buy.columns.get_loc('CashExchange')]
    specific_data_value_prompt_out = selected_rows_sell.iloc[0, selected_rows_sell.columns.get_loc('PromptExchange')]
    specific_data_value_cash_out = selected_rows_sell.iloc[0, selected_rows_sell.columns.get_loc('CashExchange')]
    
    result_dfs.append(pandas.DataFrame({
        '幣別': [currency],
        '銀行買入即期': [specific_data_value_prompt_in],
        '銀行賣出即期': [specific_data_value_prompt_out],
        '銀行買入現鈔': [specific_data_value_cash_in],
        '銀行賣出現鈔': [specific_data_value_cash_out]
    }))

# 將所有DataFrame連接成一個
result_df = pandas.concat(result_dfs, ignore_index=True)

# 導出為CSV檔案
csv_file_name = config.get('Request','time')
result_df.to_csv(csv_file_name, index=False, encoding='utf-8')

print(f'CSV檔案 {csv_file_name} 已成功生成，包含每種Currency的表格。')
</pre>  
## Run Python With GUI
### 按鈕顯示結果
<pre>
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
import subprocess

def run_other_script():
    
    try:
        # 呼叫其他 Python 腳本生成 CSV 檔案
        subprocess.call(["python", "Web_Scraping.py"])
        print('run button')
        # 讀取 CSV 檔案內容
        with open("output_currency_table.csv", "r", encoding= 'utf-8' ) as csv_file:
            csv_content = csv_file.read()
            result_label.setText(csv_content)
    except Exception as e:
        # 顯示錯誤提示
        error_message = "錯誤：" + str(e)
        QMessageBox.critical(window, "執行錯誤", error_message)

app = QApplication(sys.argv)

# 建立視窗
window = QWidget()
window.setWindowTitle("Run Python")

# 建立按鈕
print('setup button')
button = QPushButton("Web Scraping", parent=window)
button.clicked.connect(run_other_script)

# 建立標籤用於顯示結果
result_label = QLabel("Show result", parent=window)

# 建立佈局
layout = QVBoxLayout()
layout.addWidget(button)
layout.addWidget(result_label)
window.setLayout(layout)

# 顯示視窗
window.setGeometry(400, 400, 400, 400)
window.show()

sys.exit(app.exec_())
</pre>  

## CONFIG
### 調整時間
<pre>
[Request]
date = 2023-08-29
time = 2
csv_file_name = output_currency_table.csv
</pre>

