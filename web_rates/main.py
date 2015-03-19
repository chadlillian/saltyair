import	cgi
import	webapp2
import	jinja2
import	os
import	datetime
import	json
import	getrates

from google.appengine.api import users

jinja_env	=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(open('indexjson.html').read())

class stuff(webapp2.RequestHandler):
	def get(self):
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
				]
		#lines	=open('rates.csv').readlines()
		lines	=getrates.dictrates(sites)
		ret		=[]
		#keys	=lines[0].strip().split(',')
		keys	=lines[0]
		for line in lines[1:]:
			#q	=[(k,v) for k,v in zip(keys,line.strip().split(','))]
			q	=[(k,v) for k,v in zip(keys,line)]
			ret.append(dict(q))

		for i in ret:
			print i
		self.response.out.write(json.dumps(ret))


app = webapp2.WSGIApplication(	[('/', MainPage),
								 ('/data',stuff),
								],
								debug=True)
