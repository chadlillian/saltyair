#!/home/chad/anaconda/bin/python
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


import dateparser 
import datetime
import json

class clndr():
    def __init__(self):
        self.dates = {}
        self.monthnames = {'January':1, 'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}

    def addDate(self,year,month,day,am,pm):
        d = datetime.date(int(year),int(self.monthnames[month]),int(day))
        dstr = str(d)
        if dstr in self.dates.keys():
            self.dates[dstr].update({'am':am, 'pm':pm})
        else:
            self.dates[dstr] = {'am':am, 'pm':pm}

    def mergeRateCalendar(self,cal):
        for c in cal:
            dstr = str(c[0])
            if dstr in self.dates.keys():
                self.dates[dstr].update(c[1])
            else:
                self.dates[dstr] = c[1]
        
    def getCalendar(self):
        return self.dates

    def showCalendar(self):
        dates = self.dates.keys()
        dates.sort()
        for date in dates:
            print date,self.dates[date]

class propertyStats():
    def __init__(self):

        opts = Options()
        opts.add_argument('--dns-prefetch-disable')
        self.driver= webdriver.Chrome(executable_path=r"/home/chad/chromedriver",chrome_options=opts)
        #self.driver= webdriver.Firefox()
        #self.driver= webdriver.PhantomJS()

    def getReviewElements(self):
        #self.reviewtext = self.driver.find_elements_by_class_name('propreview-body')
        self.reviewstars = self.driver.find_elements_by_class_name('reviews-summary-ave')

    def getCalendar(self):
        cal = self.driver.find_elements_by_class_name('calmonth')
        today = str(datetime.date.today())

        self.calendar = clndr()
        for a in cal:
            b = a.find_elements_by_class_name('cal-date')
            monthyear = a.find_elements_by_tag_name('h3')[0].text
            if len(monthyear)>2:
                month = monthyear.split()[0]
                year = monthyear.split()[1]
                for bb in b:
                    occupancy = bb.get_attribute("class").split()
                    c = bb.find_elements_by_tag_name('a')
                    if c[0].text:
                        if 'calmonth-to-open' in occupancy:
                            am = 'NaN'
                        else:
                            am = today
                        if 'calmonth-from-open' in occupancy:
                            pm = 'NaN'
                        else:
                            pm = today
                        self.calendar.addDate(year,month,c[0].text,am,pm)
                        
    #self.calendar.showCalendar()

    def getReviews(self):
        try:
            numreviews = int(self.driver.find_elements_by_class_name('reviews-summary')[0].find_elements_by_tag_name('b')[1].text.split()[0])
            average = float(self.driver.find_elements_by_class_name('reviews-summary')[0].find_elements_by_tag_name('b')[0].text)
        except:
            srs = self.driver.find_elements_by_class_name('checkbox-label-left')
            numreviews = 0
            average = 0
            w = 5.0
            #for i,w in enumerate(srs,range(5,0,-1)):
            for i in srs:
                numreviews = numreviews+int(i.text)
                average = average+int(i.text)*w
                w = w-1
            if numreviews:
                average = float(average)/numreviews
            else:
                average = 0.0

        self.statistics['average'] = average
        self.statistics['numreviews'] = numreviews
        #print average,numreviews

            
        
    def getUnitVitals(self):
        self.getReviews()
        t1 = ['Sleeps:','Bedrooms:','Bathrooms:','Property type:']
        t2 = ['Sleeps','Bedrooms','Bathrooms','Property']
        tr = dict([(tt1,tt2) for tt2,tt1 in zip(t2,t1)])

        vitalsKeys = self.driver.find_elements_by_class_name('splitter-left')
        vitalsVals = self.driver.find_elements_by_class_name('splitter-right')

        for k,v in zip(vitalsKeys,vitalsVals):
            if k.text in t1:
                kk = tr[str(k.text)]
                self.statistics[kk] = v.text

        vitalsKeys = self.driver.find_elements_by_class_name('amenity-title')
        vitalsVals = self.driver.find_elements_by_class_name('amenity-value')

        for k,v in zip(vitalsKeys,vitalsVals):
        #    print 'amenity ',k.text
            if k.text in t2:
                self.statistics[k.text] = v.text

    def getLocation(self):
        try:
            q = self.driver.execute_script("return ownerMap")
            self.statistics['lat'] = q['lat']
            self.statistics['lng'] = q['lng']
        except:
            None

        #print 'getLocation'
        #print self.statistics

    def getManagerVitals(self):
        vitalsKeys = self.driver.find_elements_by_class_name('response-type')
        vitalsVals = self.driver.find_elements_by_class_name('response-value')
        for k,v in zip(vitalsKeys,vitalsVals):
            self.statistics[k.text] = v.text

        try:
            phone = self.driver.find_elements_by_class_name('js-phone-number')[0]
            self.statistics['phone'] = phone.find_elements_by_tag_name('b')[0].get_attribute('innerHTML')
        except:
            None

        #print 'getManagerVitals'
        #print self.statistics
        
    def getRates(self):
        parser =dateparser.table()
        ratesDates = self.driver.find_elements_by_class_name('ratelist-0')
        rates = []
        for i in range(1,7):
            a = self.driver.find_elements_by_class_name('ratelist-%i'%i)
            if a:
                rates.append(a)
        ratesc = zip(*rates)

        ratesCalendar = parser.parseElements(ratesDates,ratesc)
        self.calendar.mergeRateCalendar(ratesCalendar)
        self.statistics['calendar'] = self.calendar.getCalendar()

    def getJsonTypeB(self):
        ret = {}
        a = self.driver.find_elements_by_tag_name('script')
        for aa in a:
            z = aa.get_attribute('innerHTML')
            if 'propertytype' in z:
                for zz in z.split('\n'):
                    if zz.find('analyticsdatalayer')==0:
                        kk = zz.split('.',1)[1].split('=')[0].strip()
                        vv = zz.split('=',1)[1].split('"')[1]
                        ret[kk] = vv
            elif z.find('ownerMap')>0:
                lat = z.split('lat:')[1].split(',')[0]
                lng = z.split('lng:')[1].split(',')[0]
                
                ret['latitude'] = lat
                ret['longitude'] = lng
            elif z.find('ratePeriods')>0:
                zz = '['+z.split('[')[-1].split(']')[0]+']'
                zzz = json.loads(zz)
#            else:
#                print '%'*88
#                print z

        print ret
        return ret

                        
    def trav(self,tr,n):
        if tr.__class__ == {1:2}.__class__:
            for branch in tr.keys():
                #print '\t'*n,branch
                self.trav(tr[branch],n+1)
        return

    def getJsonTypeA(self):
        a = self.driver.find_elements_by_tag_name('script')
        for aa in a:
            z = aa.get_attribute('innerHTML')
            if 'define' in z:
                zz = z.split('define')
                for zzz in zz:
                    if 'pageData' in zzz:
                        print '#'*88
                        zzzs = '{'+zzz.split('{',1)[1].rsplit(');')[0]
                        zzzz = json.loads(zzzs)

                        self.trav(zzzz,0)

    def readProperty(self,link):

        self.driver.get(link)

        #self.getJsonTypeA()
        self.statistics = self.getJsonTypeB()


        #self.statistics = {}
        #self.getUnitVitals()
        #self.getManagerVitals()
        #self.getLocation()
        #self.getCalendar()
        #self.getRates()
        return self.statistics

    def readCalendar(self):
        self.getCalendar()
        self.getRates()
        return self.statistics['calendar']

