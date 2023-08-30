import requests
from bs4 import BeautifulSoup
import pandas
import json
import numpy

print('web scraping start')
url = 'https://www.tcb-bank.com.tw/personal-banking/deposit-exchange/exchange-rate/spot'

session = requests.Session()

response = session.get(url)
cookies = (session.cookies.get_dict())
cookies_str = ';'.join([f"{key}={value}" for key, value in cookies.items()])
# print(cookies_str)

# response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser') 
token = soup.find('input',{'name':'__RequestVerificationToken'}).get('value')
# print(token)

payload = {
        '__RequestVerificationToken': token,
        'date': '2023-08-28',
        'time': '2'
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
# print(response.json())
if response.status_code == 200:
    # 解析返回的內容
       soup = BeautifulSoup(response.content, 'html.parser')
    
    # 在這裡進行您的處理
else:
       print( response.status_code )

data = json.loads(response.text)
# df = pandas.DataFrame(
#        data["CurrencyName"],
#        index=pandas.to_datetime(
#               numpy.array(data["CurrencyName"][0])*1000),
#        columns=["123"]
#        )
# print(df[:3])


# # 轉換為pandas DataFrame
# df = pandas.DataFrame(data['result'])

# # 選擇要導出的欄位
# selected_columns = ['CurrencyName', 'Type', 'PromptExchange', 'CashExchange']
# df_selected = df[selected_columns]

# # 導出為CSV檔案
# csv_file_name = 'output.csv'
# df_selected.to_csv(csv_file_name, index=False, encoding='utf-8')

# print(f'CSV檔案 {csv_file_name} 已成功生成。')

# # 選擇特定資料的值
# specific_data_value = df.loc[df['Type'] == '買入', 'PromptExchange'].iloc[0]

# # 創建一個新的DataFrame來導出
# new_data = {
#     'SpecificValue': [specific_data_value]
# }
# new_df = pandas.DataFrame(new_data)

# # 導出為CSV檔案
# csv_file_name = 'output_specific_value.csv'
# new_df.to_csv(csv_file_name, index=False, encoding='utf-8')

# print(f'CSV檔案 {csv_file_name} 已成功生成，包含特定資料的值作為欄位值。')

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
csv_file_name = 'output_currency_table.csv'
result_df.to_csv(csv_file_name, index=False, encoding='utf-8')

print(f'CSV檔案 {csv_file_name} 已成功生成，包含每種Currency的表格。')

#----------顯示某一排---------------
# # 選擇同時滿足兩個條件的數據行
# selected_rows_in = df.loc[(df['Currency'] == 'USD') & (df['Type'] == '買入')]
# selected_rows_out = df.loc[(df['Currency'] == 'USD') & (df['Type'] == '賣出')]

# # 從篩選後的DataFrame中選擇特定數據點
# specific_data_value_prompt_in = selected_rows_in.iloc[0, selected_rows_in.columns.get_loc('PromptExchange')]
# specific_data_value_prompt_out = selected_rows_out.iloc[0, selected_rows_out.columns.get_loc('PromptExchange')]
# specific_data_value_cash_in = selected_rows_in.iloc[0, selected_rows_in.columns.get_loc('CashExchange')]
# specific_data_value_cash_out = selected_rows_out.iloc[0, selected_rows_out.columns.get_loc('CashExchange')]
# # print(f'Specific Data Value: {specific_data_value_prompt_in,specific_data_value_prompt_out,specific_data_value_cash_in,specific_data_value_cash_out}')

# # 創建包含數據的DataFrame
# data = {
#     'SpecificValue': ['幣別','銀行買入即期', '銀行賣出即期', '銀行買入現鈔', '銀行賣出現鈔'],
#     'Value': ['美金USD',specific_data_value_prompt_in, specific_data_value_prompt_out, specific_data_value_cash_in, specific_data_value_cash_out]
# }
# table_df = pandas.DataFrame(data)

# # 轉置DataFrame，將行轉換為列
# transposed_table_df = table_df.transpose()

# # 導出為CSV檔案
# csv_file_name = 'output_table1.csv'
# transposed_table_df.to_csv(csv_file_name, header=False, index=False, encoding='utf-8')

# print(f'CSV檔案 {csv_file_name} 已成功生成，包含特定數據值的表格。')
