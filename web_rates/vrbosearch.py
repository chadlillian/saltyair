#!/home/chad/anaconda/bin/python

import math
from selenium import webdriver
#from bs4 import BeautifulSoup
#from time import sleep
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

MAXPAGES = 50
DATABASE = 'VRBO_scenic_hwy_98'
COLLECTION = 'Properties'

class vrbosearch():
    def __init__(self):
        #self.driver= webdriver.Firefox()
        options = webdriver.ChromeOptions()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')

        self.driver= webdriver.Chrome(executable_path=r"/home/chad/chromedriver",chrome_options=options)
        #self.driver= webdriver.PhantomJS()

        self.client = MongoClient()

    def setup(self,database,collection):
        self.db = self.client[database]
        self.collection = self.db[collection]

        self.dbname = database
        self.collectionname = collection

    def reset(self):
        self.collection.remove({})
        self.collection = self.db[self.collectionname]

    def getNumberOfPages(self):
        wait = WebDriverWait(self.driver,10)
        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'pager')))

        pages = self.driver.find_elements_by_class_name('pager')
        self.numproperties = int(pages[0].text.split('of')[1])
        self.numpages = math.ceil(self.numproperties/50.0)

        if self.numpages > MAXPAGES:
            self.numpages = MAXPAGES

    def getVRBONumbers(self):
        wait = WebDriverWait(self.driver,10)
        try:
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'property-subtitle')))
            self.reviewtext = self.driver.find_elements_by_class_name('property-subtitle')
        except:
            self.reviewtext = []
            
        for i in self.reviewtext:
            vrbonumber = i.text.strip().strip('#')
            self.vrboNumbers.append(vrbonumber)
            try:
                self.collection.insert({'_id':vrbonumber})
            except:
                None
        
    def searchLocation(self,link):
        self.vrboNumbers = []
        self.driver.get(link)
        self.getNumberOfPages()

        t0 = time.time()
        for i in range(1,int(self.numpages)):
            pagelink = link+'&page=%i'%i
            self.driver.get(pagelink)
            self.getVRBONumbers()
            t1 = time.time()
            print t1-t0,pagelink
            t0=t1
        self.driver.quit()
        print "records found: ",self.collection.find().count()

    def getProperties(self):
        for doc in self.collection.find():
            print doc
        return self.vrboNumbers
        
if __name__=="__main__":
#    url = 'https://www.vrbo.com/vacation-rentals/usa/florida/north-west/destin?sleeps=1-plus'
    url = 'https://www.vrbo.com/vacation-rentals/usa/florida/north-west/destin/scenic-hwy-98?sleeps=1-plus'
    a = vrbosearch()
    a.setup(DATABASE,COLLECTION)
    a.searchLocation(url)
    w = a.getProperties()
