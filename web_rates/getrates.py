#!/usr/bin/python


import	os
import	sys
import	urllib2
import	re
from 	datetime	import	datetime
import	datetime
import	time
sys.path.insert(0,'beautifulsoup4-4.3.2')
from 	bs4 import BeautifulSoup as bs

class	table:
	def	__init__(self):
		self.months	=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

		return
	
	def	parseDates(self,datetext):
		x	=re.findall('([JFMASOND][aepugeco][nbrynlgptvc]\s*[0-9]+)',datetext)
		yr	=re.findall(',.*(201[4-9])',datetext)
		if not yr:
			yr	=['2015']
		if x:
			dateBeginMonth	=self.months.index(x[0].split()[0])
			dateBeginDay	=int(x[0].split()[1])
			dateEndMonth	=self.months.index(x[1].split()[0])
			dateEndDay		=int(x[1].split()[1])
			dateEndYear		=int(yr[0])

			if dateBeginMonth>dateEndMonth:
				dateBeginYear	=dateEndYear-1
			else:
				dateBeginYear	=dateEndYear

			if dateEndMonth==1 and dateEndDay==29:
				dateEndDay=28
			dateStart	=time.strptime('%s %02i %i'%(self.months[dateBeginMonth],dateBeginDay,dateBeginYear),'%b %d %Y')
			dateEnd		=time.strptime('%s %02i %i'%(self.months[dateEndMonth],dateEndDay,dateEndYear),'%b %d %Y')
		else:
			dateStart	=time.strptime('%s %02i %i'%(self.months[0],1,2015),'%b %d %Y')
			dateEnd		=time.strptime('%s %02i %i'%(self.months[0],1,2015),'%b %d %Y')

		return	{'start':dateStart, 'end':dateEnd}
	
	def	parseRates(self,rates):
		rates	=(rates.replace('$','').replace(',',''))
		return	rates

	def	getRateTable(self):
		self.table	=self.soup.find("table")
		self.datesrates	=[]
		colheaders	=['Dates','Nightly','Weekend Night',' ','Weekly','Monthly *','Event','']

		if self.table:
			for tr in self.table.find_all('tr')[2:]:
				tds	=tr.find_all('td')
				for td in tds:
					if 'class' in td.attrs.keys():
						classname	=td['class'][0]
						if classname=='ratelist-0':
							dates	=[x.text for x in td.find_all()][2]
							dates	=self.parseDates(dates)
							self.datesrates.append([dates,dict([(x,'*') for x in colheaders])])
						elif classname[:9]=='ratelist-':
							rates	=[x.text for x in td.find_all() if '$' in x.text]
							if rates:
								ci	=int(classname.split('-')[1])
								rates	=self.parseRates(rates[0])
								self.datesrates[-1][1][colheaders[ci]]	=rates

	def	readurl(self,url):
		prefix	='http://www.vrbo.com/'
		page	=urllib2.urlopen(prefix+url).read()
		self.soup	=bs(page)

		self.table	=self.soup.find("table")
		self.getRateTable()

	def	makeCalendar(self,rate):
		cal	=[]
		ret	=[]
		for i in range(1,366):
			x	='*'
			dd	=time.strptime('%03i 2015'%i,'%j %Y')
			day	=time.strftime('%b-%d-%Y',dd)
			for kk in self.datesrates:
				d1	=kk[0]['start']
				d2	=kk[0]['end']
				if d1<=dd<=d2:
					x	=kk[1][rate]

			cal.append(day)
			ret.append(x)
		return	cal,ret

	def	makeCSVTable(self,name):
		ret	=[]
		outfilename	=name+'.txt'
		out	=open(outfilename,'w')
		frmt1	='%s,%s,%s,%s,%s'
		frmt2	='%s,%s,*,*,*'
		print>>out,'#day,name,nightly,weekly,monthly'
		for i in range(1,366):
			x	=[]
			for kk in self.datesrates:
				d1	=kk[0]['start']
				d2	=kk[0]['end']
				dd	=time.strptime('%03i 2015'%i,'%j %Y')
				day	=time.strftime('%b-%d-%Y',dd)
				if d1<=dd<=d2:
					print>>out, frmt1%(day,name, kk[1]['Nightly'],kk[1]['Weekly'],kk[1]['Monthly *'])
					x	=[day,kk[1]['Nightly'],kk[1]['Weekly'],kk[1]['Monthly *']]

			if not x:
				print>>out, frmt2%(day,name)
				x	=[day,'*','*','*']
			ret.append(list(x))
		out.close()
		return	ret
		
def	compileRates(ratelist,sites):
	out	=open('comp.txt','w')
	nightly	=[]
	weekly	=[]
	monthly	=[]

	ret		=[]
	header	=['type','date']+sites
	for i,day in enumerate(ratelist[0]):
		nn	=[day[0]]
		wn	=[day[0]]
		mn	=[day[0]]
		for unit in ratelist:
			nn.append(unit[i][1])
			wn.append(unit[i][2])
			mn.append(unit[i][3])
		nightly.append(list(nn))
		weekly.append(list(wn))
		monthly.append(list(mn))

	hfrmt	=('%10s,%13s,'+'%9s,'*len(sites))[:-1]
	dfrmt	=('%10s,%13s,'+'%9s,'*len(sites))[:-1]
	print>>out,hfrmt%tuple(header)
	for l in nightly:
		dd	=['nightly']+l
		print>>out,dfrmt%tuple(dd)
	for l in weekly:
		dd	=['weekly']+l
		print>>out,dfrmt%tuple(dd)
	for l in monthly:
		dd	=['monthly']+l
		print>>out,dfrmt%tuple(dd)
	out.close()

sites	=[
'460512',
'567974',
'242896',
'369723',
'364543',
'500096',
'424099',
'225769',
'344972',
'424161',
'218220',
'3482019ha',
'3481950ha',
'3482022ha',
'3482042ha',
'253781',
'399260',
'600090',
'474807',
'586838',
'552231',
'620132',
'64895',
'305586ha',
'378729',
'481790',
'599580',
'564794',
'8452',
'129146'

		]

#			'http://www.vrbo.com/15362',
#			'http://www.vrbo.com/123233',

#sites	=[
#"77425",
#"224376",
#"75477",
#"289386",
#"188663",
#"428197",
#"65613",
#"283275",
#"69409",
#"221555",
#"119710",
#"195743",
#"128766",
#"344828",
#]

#"221548",

def	dictrates(sites):
	calendar	=[]
	names		=['date']
	for i,site in enumerate(sites):
		print site	
		t	=table()
		t.readurl(site)
		name	=site.split('/')[-1]
		dd,q	=t.makeCalendar('Weekly')
		if i==0:
			calendar.append(dd)
		calendar.append(q)
		names.append(name)
	
	cal	=zip(*calendar)
	
	ret	=[]
	ret	=[names]
	for i in cal:
		ret.append(i)
	return	ret
	
def	printrates(sites):
	calendar	=[]
	names		=['date']
	for i,site in enumerate(sites):
		print site	
		t	=table()
		t.readurl(site)
		name	=site.split('/')[-1]
		dd,q	=t.makeCalendar('Weekly')
		if i==0:
			calendar.append(dd)
		calendar.append(q)
		names.append(name)
	
	cal	=zip(*calendar)
	
	out	=open('rates.csv','w')
	frmt	='%s'+',%s'*(len(calendar)-1)
	print>>out, frmt%tuple(names)
	for i in cal:
		print>>out, frmt%tuple(i)
	
	out.close()

if __name__=="__main__":
#	sites	=[
#	'460512',
#	'567974',
#			]
	
#	a	=dictrates(sites)
	a	=printrates(sites)


