from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from random import randint, shuffle


class QuillBot:
    def __init__(self):
        pass

    def init(self, headless=True):
        try: 
            self.options = Options()
            self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
            self.options.add_argument(f'user-agent={self.user_agent}')
            self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
            if headless: self.options.add_argument('--headless')

            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
            self.driver.get('http://quillbot.com')
            return '@g;QuillBot initialized successfully@e;.'
        except: 
            self.driver = False
            return '@y;Can\'t get to quillbot right now, will try again later.'

    def quillbot_phrasing(self, string):
        WebDriverWait(self.driver, timeout=30).until(EC.presence_of_element_located((By.ID, 'inputText')))
        input = self.driver.find_element(By.ID, 'inputText')
        output = self.driver.find_element(By.ID, 'outputText')

        input.clear(), input.send_keys(string), input.send_keys(Keys.CONTROL + Keys.ENTER)
        WebDriverWait(self.driver, timeout=30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'quillArticleBtn')))
        return {'description': output.text, 'msg': '@g;Description shuffled using QUILLBOT@e;'}
    
    def manual_phrasing(self, string, shuf=False):
        string = string.split('. ')
        if shuf: shuffle(string)
        return {'description': '. '.join(string[:randint(2 if len(string) > 1 else len(string),len(string))]), 'msg': '@y;Description shuffled MANUAL@e;'}

    def handle_phrasing(self, string,  shuf=False, refresh_count=3):
        if self.driver:
            try: return self.quillbot_phrasing(string)
            except:
                self.driver.refresh()
                if refresh_count: return self.handle_phrasing(string, refresh_count-1, shuf) 
        
        elif not self.driver and refresh_count:
            try:
                print('Retrying QuillBot description paraphraser...')
                self.init()
                return self.handle_phrasing(string, 0, shuf)
            except: pass

        return self.manual_phrasing(string, shuf)

    def done(self):
        try:
            self.driver.close()
            self.driver.quit()
        except: pass