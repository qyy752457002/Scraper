from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import argparse
import json
import time

class SeleniumScraper():

    def __init__(self, driver):
        self.driver = driver
        self.web_data = dict()

    def Browse_CNN(self):
        self.driver.get('https://edition.cnn.com/')
        self.driver.maximize_window()

        # collect all topics' web elements
        topics = self.driver.find_elements(by=By.CSS_SELECTOR, value = '[data-analytics="header_top-nav"]')

        # store urls from topics' web elements
        urls = []

        # store topic names
        topic_dic = dict()

        # iterate over each topic to get topic name and its url
        for topic_element in topics:
            topic_name = topic_element.get_attribute("innerText")
            if topic_name == '':
                continue
            topic_dic[topic_name] = []
            url = topic_element.get_attribute('href')
            urls.append(url)

        # iterate over each topic's url
        for index, url in enumerate(urls):

            topic = list(topic_dic.keys())[index]

            self.driver.get(url)

            # wait for articles' web elements to load
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, "cd__headline"))
                WebDriverWait(driver, 2).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")

            # save urls from articles' web elements
            article_urls = set()

            try:
                elements = self.driver.find_elements(by=By.CLASS_NAME, value = "cd__headline")
                
                for element in elements:
                    try:
                        url = element.find_element(by=By.TAG_NAME, value = "a").get_attribute("href")
                        article_urls.add(url)
                    except NoSuchElementException:
                        continue
                    
            except NoSuchElementException:
                continue

            counter = 0
            limit = 30

            # iterate over each article's url
            # for each topic, only up to 30 articles will be collected considering the appropriate workload of mini project
            for item in article_urls:

                if type(item) != str:
                    continue

                try:
                    self.driver.get(item)
                except WebDriverException:
                    continue

                title = ""
                author = ""
                post_time = ""
                paragraphs = ""
                
                try:
                    # get body paragraphs
                    paragraph_elements = self.driver.find_elements(by=By.CLASS_NAME, value = "zn-body__paragraph")
                    paragraphs = "".join([element.get_attribute("innerText") for element in paragraph_elements])
                    if paragraphs == "":
                        continue
                # if the article does not exist on the current page, then go to the next url
                except NoSuchElementException:
                    continue

                article = dict()

                try:
                    # get the title of the article
                    title = self.driver.find_element(by=By.CLASS_NAME, value = 'pg-headline').get_attribute("innerText")
                except NoSuchElementException:
                    print("no title found")

                try:
                    # get the author of the article
                    author = self.driver.find_element(by=By.CLASS_NAME, value = 'metadata__byline__author').get_attribute("innerText")
                except NoSuchElementException:
                    print("no authors found")

                try:
                    # get post time
                    post_time = self.driver.find_element(by=By.CLASS_NAME, value = 'update-time').get_attribute("innerText")
                except NoSuchElementException:
                    print("no post time found")

                article['url'] = item
                article['title'] = title
                article['author'] = author
                article['post_time'] = post_time
                article['article'] = paragraphs
                
                # add current article to topic_dic
                topic_dic[topic].append(article)

                print(article)

                counter += 1
                if counter == limit:
                    break

        # add current website's data to web_data
        self.web_data['CNN'] = topic_dic

    def Browse_ABC(self):

        self.driver.get('https://www.abc.net.au/news/')
        self.driver.maximize_window()

        # collect all topics' web elements
        topics = self.driver.find_elements(by=By.CSS_SELECTOR, value = '[class="_10pc5 BgVdI"]')

        # Accept Cookies on the website
        try:
            button = self.driver.find_element(by=By.CSS_SELECTOR, value = '[data-component="CookieBanner_AcceptAll"]')
            button.click()
        except NoSuchElementException:
            pass

        # store urls from topics' web elements
        urls = []

        # store topic names
        topic_dic = dict()

        # iterate over each topic to get topic name and its url
        for topic_element in topics:
            topic_name = topic_element.get_attribute("innerText")
            if topic_name == '':
                continue
            topic_dic[topic_name] = []
            url = topic_element.get_attribute('href')
            urls.append(url)

        print(topic_dic)

        # iterate over each topic's url
        for index, url in enumerate(urls):

            topic = list(topic_dic.keys())[index]

            self.driver.get(url)

            # wait for articles' web elements to load
            try:
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '[class="_3T9Id fmhNa nsZdE _2c2Zy _1tOey _3EOTW"]'))
                WebDriverWait(driver, 2).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")

            try:
                # collect artcles' web elements based on tag name
                articles = self.driver.find_elements(by=By.CSS_SELECTOR, value = '[class="_3T9Id fmhNa nsZdE _2c2Zy _1tOey _3EOTW"]')
            except NoSuchElementException:
                continue
                
            # save urls from articles' web elements
            article_urls = set()

            # iterate over each article to get url
            for article_element in articles:
                article_url = article_element.get_attribute("href")
                article_urls.add(article_url)

            counter = 0
            limit = 30
            
            # iterate over each article's url
            # for each topic, only up to 30 articles will be collected considering the appropriate workload of mini project
            for item in article_urls:

                if type(item) != str:
                    continue

                try:
                    self.driver.get(item)
                except WebDriverException:
                    continue

                title = ""
                author = ""
                post_time = ""
                paragraphs = ""

                try:
                    # get body paragraphs                               
                    paragraph_elements = self.driver.find_elements(by=By.CLASS_NAME, value = "_1HzXw")
                    paragraphs = "".join([element.get_attribute("innerText") for element in paragraph_elements])
                    if paragraphs == "":
                        continue
                # if the article does not exist on the current page, then go to the next url
                except NoSuchElementException:
                    continue

                article = dict()

                try:
                    # get the title of the article
                    title = self.driver.find_element(by=By.TAG_NAME, value = 'h1').get_attribute("innerText")
                except NoSuchElementException:
                    print("no title found")

                try:
                    # get the author of the article                     
                    author = self.driver.find_element(by=By.CSS_SELECTOR, value = '[class="fmhNa nsZdE _2c2Zy _1tOey _5sx7T"]').get_attribute("innerText")
                except NoSuchElementException:
                    print("no authors found")

                try:
                    # get post time
                    post_time = self.driver.find_element(by=By.CSS_SELECTOR, value = '[data-component="Timestamp"]').get_attribute("innerText")
                except NoSuchElementException:
                    print("no post time found")

                article['url'] = item
                article['title'] = title
                article['author'] = author
                article['post_time'] = post_time
                article['article'] = paragraphs
                
                # add current article to topic_dic
                topic_dic[topic].append(article)

                print(article)

                counter += 1
                if counter == limit:
                    break

        # add current website's data to web_data
        self.web_data['ABC'] = topic_dic

    def Save_to_json(self, title):

        path = "./"
        filePathNameWExt = os.path.join(path, title + '.json')

        with open(filePathNameWExt, 'w') as fp:
      
            json_str = json.dumps(self.web_data[title])
            fp.write(json_str)
            
    def Quit(self):
        self.driver.quit()
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser("configure the driver")
    parser.add_argument("path", help = "your driver's path", type = str)
    args = parser.parse_args()
    
    # my local driver path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    s = Service(args.path)
    driver = webdriver.Chrome(service = s)
    scraper = SeleniumScraper(driver)
    scraper.Browse_ABC()
    scraper.Save_to_json('ABC')
    scraper.Browse_CNN()
    scraper.Save_to_json('CNN')
    scraper.Quit()
