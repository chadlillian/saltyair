#!/home/chad/anaconda/bin/python
import urllib2
import sys
from   bs4 import BeautifulSoup as bs
from datetime import datetime
from datetime import date
from datetime import timedelta
import json
from dateutil.parser import parse
import pandas as pd
import time

class propertyStats():
    def __init__(self):
        None

    def getUnitData(self,html):
        ret = {}
        for zz in html.split('\n'):
            if zz.find('analyticsdatalayer')==0:
                kk = zz.split('.',1)[1].split('=')[0].strip()
                vv = zz.split('=',1)[1].split('"')[1]
                ret[kk] = vv
        return ret

    def getRating(self,html):
        ret = {}
        zz = html.split(',')
        for zzz in zz:
            if zzz.find('ratingValue')>0:
                ret['average'] = float(zzz.split('"')[3])

        return ret

    def getMapData(self,html):
        ret = {}
        lat = html.split('lat:')[1].split(',')[0]
        lng = html.split('lng:')[1].split(',')[0]
        
        ret['latitude'] = lat
        ret['longitude'] = lng

        return ret
        
    def getOccupancyCalendar(self,html):
        ret = {}
        availability = html.split('"availability"')[1].split('"')[1]
        startdate = parse(html.split('"beginDate"')[1].split('"')[1])
        q = dict([((startdate+timedelta(i)).strftime('%Y-%m-%d'),a) for i,a in enumerate(availability)])
        calendar = pd.DataFrame(q.items(),columns=['date','occupied'])
        #ret['unitAvailability'] = calendar
        ret['unitAvailability'] = q

        return ret

    def getRateDates(self,html):
        zz = '['+html.split('[')[-1].split(']')[0]+']'
        zzz = json.loads(zz)
        return zzz

    def getJsonTypeB(self):
        ret = {}
        #ret['average'] = 'X' 
        #ret['numreviews'] = 0

#       get rate calendar
        b = zip(*[self.soup.findAll('td',attrs={'class':'ratelist-'+str(i)}) for i in [1,4,5]])
        calendar = []
        for bb in b:
            calendar.append({'nightly':bb[0].string,'weekly':bb[1].string,'monthly':bb[2].string})

        a = self.soup.findAll('script')
        for aa in a:
            z = aa.string
            if z:
                if 'propertytype' in z:
                    r = self.getUnitData(z)
                    ret.update(r)
                elif z.find('ownerMap')>0:
                    r = self.getMapData(z)
                    ret.update(r)
                elif z.find('ratePeriods')>0:
                    r = self.getRateDates(z)
                    for rr,cc in zip(r,calendar):
                        rr.update(cc)
                    ret['ratePeriods'] = r
                elif z.find('aggregateRating')>0:
                    r = self.getRating(z)
                    ret.update(r)
                elif z.find('unitAvailability')>0:
                    r = self.getOccupancyCalendar(z)
                    ret.update(r)
        return ret

    def trav(self,tr,n):
        if tr.__class__ == {1:2}.__class__:
            for branch in tr.keys():
                #print '\t'*n,branch,tr[branch]
                self.trav(tr[branch],n+1)
        return

    def getJsonTypeA(self):
        #a = self.driver.find_elements_by_tag_name('script')
        ret = {}
        a = self.soup.findAll('script')
        for aa in a:
            #z = aa.get_attribute('innerHTML')
            z = aa.string
            if z and 'define' in z:
                zz = z.split('define')
                for zzz in zz:
                    if 'pageData' in zzz:
                        zzzs = '{'+zzz.split('{',1)[1].rsplit(');')[0]
                        print zzzs
                        zzzz = json.loads(zzzs)

                        ret = {'average':zzzz['unit']['averageRating'], 'numreviews':zzzz['listing']['reviewCount']}
        
        return ret
                        

    def readProperty(self,link):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7'}
        request = urllib2.Request(link, '', headers)
        self.page = urllib2.urlopen(request).read()

        #self.page = urllib2.urlopen(link).read()
        self.soup = bs(self.page)

        statsA = self.getJsonTypeA()
        statsB = self.getJsonTypeB()
        self.statistics = statsA.copy()
        self.statistics.update(statsB)

        #self.statistics = {}
        #self.getCalendar()
        return self.statistics

