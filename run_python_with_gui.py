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
