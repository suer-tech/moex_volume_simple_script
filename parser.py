from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


chrome_options = Options()
service = Service(executable_path=ChromeDriverManager().install())

chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=service, options=chrome_options)


def get_parse_data(ticker):
    url = 'https://trading.finam.ru/profile/MOEX-MOEX'
    driver.get(url)

    search_xpath = '//*[@id="search-panel"]/svg/path[2]'
    search = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, search_xpath)))
    search.click()

    search_input_xpath = '//*[@id="search-issue-input"]'
    search_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, search_input_xpath)))
    search_input.send_keys(ticker)

    search_result_xpath = '//*[@id="search-result"]/div[1]/div[2]'
    search_result = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, search_result_xpath)))
    search_result.click()

    wait = WebDriverWait(driver, 10)

    oborot_xpath = '//*[@id="security-details-content"]/div/div[3]/div[10]/p[2]'
    oborot = wait.until(EC.visibility_of_element_located((By.XPATH, oborot_xpath))).text

    price_close_xpath = '//*[@id="security-details-content"]/div/div[3]/div[7]/p[2]'
    price_close = wait.until(EC.visibility_of_element_located((By.XPATH, price_close_xpath))).text
    return [oborot, price_close]


def format_number(input_str):
    # Удаляем все знаки "."
    input_str = input_str.replace('.', '')

    # Заменяем "," на "."
    input_str = input_str.replace(',', '.')

    # Оставляем два знака после разделителя "."
    if '.' in input_str:
        parts = input_str.split('.')
        if len(parts) == 2:
            input_str = f"{parts[0]}.{parts[1][:2]}"

    return input_str