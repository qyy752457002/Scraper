from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import psycopg2
from psycopg2.extensions import AsIs
from psycopg2 import sql
import argparse

class SeleniumScraper():

    def __init__(self, driver):
        self.driver = driver
        self.CNN_data = dict()
        self.ABC_data = dict()

    def Browse_CNN(self):
        self.driver.get('https://edition.cnn.com/')

        # collect all topics' web elements
        topics = self.driver.find_elements(by=By.CSS_SELECTOR, value = '[data-analytics="header_top-nav"]')

        # store urls from topics' web elements
        urls = []

        # iterate over each topic to get topic name and its url
        for topic_element in topics:
            topic_name = topic_element.get_attribute("innerText")
            if topic_name == '':
                continue
            self.CNN_data[topic_name] = []
            url = topic_element.get_attribute('href')
            urls.append(url)

        # iterate over each topic's url
        for index, url in enumerate(urls):

            topic = list(self.CNN_data.keys())[index]

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

                title = "NULL"
                author = "NULL"
                post_time = "NULL"
                paragraphs = ""

                check = False
                
                try:
                    # get body paragraphs
                    paragraph_elements = self.driver.find_elements(by=By.CLASS_NAME, value = "zn-body__paragraph")

                    try:
                        paragraphs = "".join([element.get_attribute("innerText") for element in paragraph_elements])
                    except StaleElementReferenceException:
                        check = True
                    
                # if the article does not exist on the current page, then go to the next url
                except NoSuchElementException:
                    continue

                if check or paragraphs == "":
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
                
                # add current article
                self.CNN_data[topic].append(article)

                print(article)

                counter += 1
                if counter == limit:
                    break

            self.Create_Insert_Table(self.CNN_data, topic)

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

        # iterate over each topic to get topic name and its url
        for topic_element in topics:
            topic_name = topic_element.get_attribute("innerText")
            if topic_name == '':
                continue
            self.ABC_data[topic_name] = []
            url = topic_element.get_attribute('href')
            urls.append(url)

        # iterate over each topic's url
        for index, url in enumerate(urls):

            topic = list(self.ABC_data.keys())[index]

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

                title = "NULL"
                author = "NULL"
                post_time = "NULL"
                paragraphs = ""

                check = False

                try:
                    # get body paragraphs                               
                    paragraph_elements = self.driver.find_elements(by=By.CLASS_NAME, value = "_1HzXw")

                    try:
                        paragraphs = "".join([element.get_attribute("innerText") for element in paragraph_elements])
                    except StaleElementReferenceException:
                        check = True
                    
                    # if the article does not exist on the current page, then go to the next url
                except NoSuchElementException:
                    continue

                if check or paragraphs == "":
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
                
                # add current article
                self.ABC_data[topic].append(article)

                print(article)

                counter += 1
                if counter == limit:
                    break

            self.Create_Insert_Table(self.ABC_data, topic)

    def Create_Insert_Table(self, data, name):
        
	# create tables in the PostgreSQL database

        query = """
            CREATE TABLE IF NOT EXISTS %(table)s (
                URL TEXT NOT NULL PRIMARY KEY,
                TITLE TEXT NOT NULL,
                AUTHOR TEXT NOT NULL,
                POST_TIME TEXT NOT NULL,
                ARTICLE TEXT NOT NULL )
   
                """

        # keep the table name lowercased without blank space
        table_name = "".join(name.split()).lower()
        
        hostname = 'scraper-db.cpxwep3plgox.us-east-1.rds.amazonaws.com'
        database = 'testDB'
        username = 'postgres'
        pwd = 'qyy2614102'
        port_id = 5432

        conn = None
        cur = None
	
        try:
            conn = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id )

            cur = conn.cursor()
		
            # create a table
            cur.execute(query, {'table': AsIs(table_name)})
            print('Table created: ', table_name)

            # insert data
            insert_script = sql.SQL('INSERT INTO {table} (URL, TITLE, AUTHOR, POST_TIME, ARTICLE) VALUES(%s, %s, %s, %s, %s)').format(table=sql.Identifier(table_name))
            insert_values = [list(dic.values()) for dic in data[name]]
            for record in insert_values:
                cur.execute(insert_script, record)	    

            conn.commit()
	    
        except Exception as error:
            print(error)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
        
    def Quit(self):
        self.driver.quit()
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser("configure the driver")
    parser.add_argument("path", help = "your driver's path", type = str)
    args = parser.parse_args()
    
    # my local driver path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    s = Service(args.path)
    driver = webdriver.Chrome(service = s)

    # set English as chromdriver's defult language
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    
    scraper = SeleniumScraper(driver)
    scraper.Browse_ABC()
    scraper.Browse_CNN()
    scraper.Quit()
