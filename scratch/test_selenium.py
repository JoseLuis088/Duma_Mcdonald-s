import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

driver.get("http://127.0.0.1:8000")
time.sleep(2)
for entry in driver.get_log('browser'):
    print(entry)

driver.quit()
