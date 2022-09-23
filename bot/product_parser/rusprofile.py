from copy import copy
import time
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bot.utils.logging import log

from . import config

info = {
    'status' : '',
    'company_name' : '',
    'company_status' : '',
    'realiability' : '',
    'company_inn' : '',
    'company_kpp' : '',
    'company_ogrn' : '',
    'table_status' : ''
}

class RusProfileParser:
    options: Options
    
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument(f"user-agent={config.user_agent}")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--headless')
        self.options.add_argument("--window-size=1366,768")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(chrome_options=self.options)
        
    def quit(self) -> None:
        self.driver.quit()    
    
    def search_by_inn(self, inn: str) -> dict:
        company_info = copy(info)
        self.driver.get(config.rusprofile_url.format(search=inn))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_page = soup.find('div', {'id' : 'main', 'class' : 'company-main'})
        page_status = main_page.find('div', {'class' : 'container search-result__container'})
        
        if page_status is None:
            company_info['status'] = 'OK'
            company_info['company_name'] = main_page.find('h1', {'itemprop' : 'name'}).string[2:].strip()
            if company_info['company_name'][:2] == 'ИП':
                company_info['company_inn'] = main_page.find('span', {'id' : 'clip_inn'}).string
                company_info['company_kpp'] = None
                company_info['company_ogrn'] = main_page.find('span', {'id' : 'clip_ogrnip'}).string
                company_info['table_status'] = '1'
                company_info['realiability'] = 'OK'
                company_info['company_status'] = 'OK'
                return company_info
            company_info['table_status'] = '2' if 'ООО' in company_info['company_name'] else '1'
            company_info['company_status'] = main_page.find('div', {'class' : 'company-status active-yes'})
            if company_info['company_status'] is None:
                company_info['company_status'] = 'ERROR'
                return company_info
            else:
                company_info['company_status'] = 'OK'
            company_info['realiability'] = main_page.find('a', {'class' : 'rely-tile-badge'}).string.lower()
            if company_info['realiability'] not in ('высокая', 'средняя'):
                company_info['realiability'] = 'ERROR'
                return company_info
            
            company_info['company_inn'] = main_page.find('span', {'id' : 'clip_inn'}).string
            company_info['company_kpp'] = main_page.find('span', {'id' : 'clip_kpp'}).string
            company_info['company_ogrn'] = main_page.find('span', {'id' : 'clip_ogrn'}).string

            # self.driver.save_screenshot(f'screenshots/{screenshot_filename}')

            return company_info
        else:
            company_info['status'] = 'ERROR'
            return company_info
        
    def screenshot_webpage(self, url: str, screenshot_filename: str) -> None:
        try:
            self.driver.get(url)
            while True:
                page_state = self.driver.execute_script('return document.readyState;')
                if page_state == 'complete':
                    break
                time.sleep(0.5)
            self.driver.save_screenshot(f'screenshots/{screenshot_filename}')
        except Exception as e:
            log.error(f'Ошибка! Невозможно сделать скриншот. {e}')
            