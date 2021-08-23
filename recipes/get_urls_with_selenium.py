from selenium import webdriver
import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select

# url = "https://www.allrecipes.com/recipes/14485/healthy-recipes/main-dishes/chicken/?page=2"
url = "https://www.allrecipes.com/recipes/16375/healthy-recipes/desserts/?page=2"
opts = Options()
opts.add_argument("--incognito")
opts.add_argument("--disable-popup-blocking")
opts.headless =True
driver = Chrome(options=opts)
driver.get(url)


all_links = []
def url_grabber(driver):
    while True:
        if 'page=2' in driver.current_url:
            try:
                linklist = driver.find_elements_by_xpath("/html/body/main/div[2]/div/div[*]/div[2]/div/a")
                links = [s.get_attribute('href') for s in linklist] 
                next_page = driver.find_element_by_xpath("/html/body/main/div[2]/div/div[29]/a[2]")
                next_page.click()
            except ElementClickInterceptedException:
                popup = driver.find_element_by_xpath("/html/body/div[12]/div/div[2]/div[2]/button[1]")
                popup.click()
                linklist = driver.find_elements_by_xpath("/html/body/main/div[2]/div/div[*]/div[2]/div/a")
                links = [s.get_attribute('href') for s in linklist] 
                next_page = driver.find_element_by_xpath("/html/body/main/div[2]/div/div[29]/a[2]")
                next_page.click()
            all_links.append(links)

                    
        else:
            driver.implicitly_wait(45)
            linklist = driver.find_elements_by_xpath("/html/body/main/div[2]/div/div[*]/div[2]/div/a")
            links = [s.get_attribute('href') for s in linklist]
            all_links.append(links)
            if len(driver.find_elements_by_xpath("/html/body/main/div[2]/div/div[29]/a[*]"))==2: # 2 buttons(prev,next)
                next_page = driver.find_element_by_xpath("/html/body/main/div[2]/div/div[29]/a[2]")
                next_page.click()
            else:
                driver.quit()
                break

         
        
    return  all_links


result = url_grabber(driver)

df = pd.DataFrame(result).T
names = [f'page-{i}' for i in range(2,len(result)+2)]
df.columns = names
# df.to_csv('chicken_urls.csv', index=False, header=True)
df.to_csv('/home/zelalem/my_repos/mygithubrepos/vacation-projects/recipes/dessert_urls.csv', index=False, header=True)