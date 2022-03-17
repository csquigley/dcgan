#imports
import undetected_chromedriver.v2 as uc
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import random
import requests
import mimetypes
import re
from PIL import Image

#basic variables
search_terms = "Chinese Traditional Painting"
base_url = "https://www.google.co.kr/imghp?hl=en&ogbl"
xpath = "//*[@id='sbtc']/div[1]/div/div[2]/input"
full_xpath = "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input"
photo_xpath = "//*[@id='islrg']/div[1]/div/a[1]"
common_file_types = ["JPG","PNG","GIF","WEBP","TIFF","PSD","RAW","BMP","HEIF","INDD"]
common_file_types = [ty.lower() for ty in common_file_types]
start = 0

#define a regex function to transform search results into usable links.
def strip_image_url(url):
    search_pattern = "=https[\S]+"
    s = re.search(search_pattern,url)
    s = s.group(0)[1:]
    search_pattern =  "^.*?(?=&)"
    s = re.search(search_pattern,s)
    s = s.group(0).replace("%3A",":").replace("%2F","/")
    return s

#instantiate driver
driver = uc.Chrome(version_main=98)
#attempt to get google images
for st in search_terms:
    try:
        driver.get(base_url)
    except Exception as e:
        print("base_url didn't work")
        print(e)
    #find the google search box and select it
    try:
        google_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    except Exception as e:
        #try the alternative xpath if the initial xpath doesn't work
        try:
            google_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, full_xpath)))
        except Exception as e:
            print(e)

    try:
        #enter the search terms and click the enter key
        google_input.send_keys(st)
        sltime = 3*random.random()
        time.sleep(sltime)
        google_input.send_keys(Keys.ENTER)
    except Exception as e:
        print(e)
    #sleep for 5 seconds to help ensure the page loads.
    time.sleep(5)
    #scroll to the bottom of  the search results
    for i in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sltime = 5*random.random()
        time.sleep(sltime)
    #get the xpath of all the photos on the page
    try:
        urls = WebDriverWait(driver,30).until(EC.presence_of_all_elements_located((By.XPATH,photo_xpath)))
        print(f"Total Links: {len(urls)}")
        time.sleep(5)
    except Exception as e:
        print(e)

    for i,el in enumerate(urls):
        i = i + start
        if i < len(urls):
            time.sleep(5*random.random())
            try:
                #photo previews must be clicked to load  the link
                el.click()
                #after clicking, get the href (source) of the photo
                href = el.get_attribute('href')
                #pass the result into the function designed above.
                href = strip_image_url(href)
                #get the final three characters
                filetype = href[-3:].lower()
                #check if the type is in filetypes
                if filetype not in common_file_types:
                    href = el.get_attribute('href')
                    #if it isn't print the href to find out why
                    print(href)
                else:
                    #get the photo with request and
                    f = requests.get(href,allow_redirects=True)
                    path_name = f"photos/photo_{i}.{filetype}"
                    open(path_name,'wb').write(f.content)
                    time.sleep(5*random.random())

            except Exception as e:
                print(e)
        else:
            break

time.sleep(25)
driver.close()
