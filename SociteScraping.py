from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time 
import os
import zipfile

class SociteScraping:
    
    def __init__(self, siret = None, proxy=None):
        self.url = 'https://www.societe.com/'
        self.SIRET = siret

        self.with_proxy = True
        if self.with_proxy :
            self.PROXY_HOST = proxy["PROXY_HOST"] # rotating proxy or host
            self.PROXY_PORT = proxy["PROXY_PORT"] # port
            self.PROXY_USER = proxy["PROXY_USER"] # username
            self.PROXY_PASS = proxy["PROXY_PASS"] # password
            self.options = self.get_options_for_proxy()
        else:
            self.options = webdriver.ChromeOptions()
            
        self.with_selenium_grid = True
        if self.with_selenium_grid:
            # IP address and port and server of the Selenium hub and browser options
            self.HUB_HOST = "localhost"
            self.HUB_PORT = 4444
            self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
            self.driver = webdriver.Remote(command_executor=self.server, options=self.options)
        else:
            self.driver = webdriver.Chrome(options=self.options)
            
        # self.start_scraping()
        

    def get_options_for_proxy(self):
        
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS)
        
        def get_chrome_options(use_proxy=True, user_agent=None):
            chrome_options = webdriver.ChromeOptions()
            if use_proxy:
                pluginfile = 'proxy_auth_plugin.zip'
        
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                chrome_options.add_extension(pluginfile)
            if user_agent:
                chrome_options.add_argument('--user-agent=%s' % user_agent)
            
            return chrome_options
        return get_chrome_options()
    
    def start_scraping(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
             )

            input_search = self.get_element("/html/body/div[2]/header/div[2]/div[2]/div/form/div[1]/div[1]/input")
            if input_search["status"]:
                input_search = input_search["data"]
                input_search.send_keys(self.SIRET)
                input_search.submit()
            else:
                return {"status": False, "data":input_search["data"] }
                
            button_modal = self.get_element('/html/body/div[1]/div/div/div/div/div/div[3]/button[2]')
            if button_modal["status"]:
                button_modal = button_modal["data"]
                button_modal.click()
            else:
                return {"status": False, "data":button_modal["data"] }
            
            
            first_societe = self.get_element('//*[@id="result_deno_societe"]/div/div/a')
            if first_societe["status"]:
                first_societe = first_societe["data"]
                first_societe.click()
            else:
                return {"status": False, "data":first_societe["data"] }


            effectif_elem = self.get_element('//*[@id="trancheeff-histo-description"]')
            capital_elem = self.get_element('//*[@id="capital-histo-description"]')
            gerant_elem = self.get_element('//*[@class="Table leader"]/tbody/tr/td[2]/a/span')

            if not effectif_elem["status"] and not capital_elem["status"] and not gerant_elem["status"] :
                return {"status": False, "data": f"3*ERROR : {str(effectif_elem["data"])}" }
                
            print(self.SIRET)
            print(f"      {effectif_elem["data"].text if effectif_elem["status"] else None}")
            print(f"      {capital_elem["data"].text if capital_elem["status"] else None}")
            print(f"      {gerant_elem["data"].text if gerant_elem["status"] else None}")

            result = {
                "effectif" : effectif_elem["data"].text if effectif_elem["status"] else None,
                "capital" : capital_elem["data"].text if capital_elem["status"] else None,
                "gerant" : gerant_elem["data"].text if gerant_elem["status"] else None
            }
            
            return {"status": True, "data": result }
            
        except Exception as e:
            print(f"Error : {e}")
            return {"status": False, "data": str(e) }
        finally :
            self.driver.quit()
            
    def get_element(self, path_to_elem, class_=None):
        i = 0
        while i<5:
            try:
                if not class_:
                    elem = self.driver.find_element(By.XPATH, path_to_elem)
                    return {"status": True, "data":elem }
            except Exception as e:
                i += 1
                if i == 5:
                    return {"status": False, "data":str(e) }