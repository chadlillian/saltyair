import	cgi
import	webapp2
import	jinja2
import	os
import	datetime
#import	json

from google.appengine.api import users

jinja_env	=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(open('index.html').read())

class contractbuilder(webapp2.RequestHandler):
	def	write(self):
		self.data	={}
		self.fields	=['firstname','lastname','indate','outdate',\
						'numadults','numchild','rentalfee','cleaningfee',\
						'tax','deposit', 'depOrIns', 'securitydeposit']

		for f in self.fields:
			self.data[f]	=self.request.get(f)

		for f in self.fields:
			print f,self.data[f]


	def	post(self):
		jinja_env	=jinja2.Environment(\
			loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
		self.write()
		template	=jinja_env.get_template('contract.html')

		if self.data['depOrIns']=='deposit':
			rentalcost	=float(self.data['rentalfee'])+float(self.data['cleaningfee'])+float(self.data['tax'])
			totalcost	='$%.2f (Rental Fee:$%.2f, Cleaning Fee: $%.2f, County Bed Tax: $%.2f)'%(rentalcost, float(self.data['rentalfee']),float(self.data['cleaningfee']),float(self.data['tax'])) 
			deposit		='$%.2f'%(float(self.data['securitydeposit']))
			spdep		=float(self.data['securitydeposit'])
			ins			=0.0
		elif self.data['depOrIns']=='insurance':
			rentalcost	=float(self.data['rentalfee'])+float(self.data['cleaningfee'])+float(self.data['tax'])+float(self.data['securitydeposit'])
			totalcost	='$%.2f (Rental Fee:$%.2f, Cleaning Fee: $%.2f, Damage Insurance: $%.2f, County Bed Tax: $%.2f)'%(rentalcost, float(self.data['rentalfee']),float(self.data['cleaningfee']),float(self.data['securitydeposit']),float(self.data['tax'])) 
			deposit		='N/A'
			spdep		=0.0
			ins			=float(self.data['securitydeposit'])

		adults		=int(self.data['numadults'])
		child		=int(self.data['numchild'])

		print self.request.get("numchildmenu")

		guestnum	='%i adult'%(adults)+'s'*(adults>1)
		if child==1:
			guestnum	=guestnum+', 1 child'
		elif child>1:
			guestnum	=guestnum+', %i children'%(child)



		today		=datetime.date.today().strftime('%A %B %d %Y')
		checkin		=datetime.datetime.strptime(self.data['indate'],'%Y-%m-%d').strftime('%A %B %d %Y')
		checkout	=datetime.datetime.strptime(self.data['outdate'],'%Y-%m-%d').strftime('%A %B %d %Y')

		firstpayment	=round((rentalcost+ins)/2.0,2)
		secondpayment	=round(rentalcost-firstpayment+spdep,2)

		data	={	"guestname"		:self.data['firstname'].capitalize()+' '+self.data['lastname'].capitalize(),
					"today"			:today,
					"arrivaldate"	:checkin,
					'departuredate'	:checkout,
					'numberguests'	:guestnum,
					'totalcost'		:totalcost,
					'firstpayment'	:'$%.2f'%(firstpayment),
					'secondpayment'	:'$%.2f'%(secondpayment),
					'damagedeposit'	:deposit,
				}

					
		outputtext	=template.render(data)
		self.response.out.write(outputtext)

app = webapp2.WSGIApplication(	[('/', MainPage),
                              	('/sign', contractbuilder)
								],
								debug=True)

