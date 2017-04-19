# Scraper operations:

# Check the days that a user wants to be notified
# 	combine those into unique set
# for each day and site check status
# 	if status has changed or doesn't exist
# 		notify
# 	if status has not changed
# 		pass


# How do I tell if someone wants a site and a day?
# 	target dates will have user and date and site
# 	join target dates with active users and build a dataset
# 	maybe just iterate through each day.

# 	Build something that lets users edit their target dates and 

# want to have this: a dictionary with
# 	{
# 		date:{
# 			site1:{
# 				users:[all the users]
# 			},
# 			site2:{}
# 		}
# 	}

# so users can do the following:
# 	add dates to target_dates
# 	check what dates they want for a park or all parks
# 	remove dates
import sqlite3 as sql 
import py_utils as pu
import smtplib
import datetime
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import re

creds=pu.load_credentials()
cj = cookielib.LWPCookieJar()
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


dictionary_query="""
select
	t.date,
	cs.site,
	cs.url,
	cs.park,
	con.name,
	con.email
from
	contacts con
	inner join target_dates t
		on t.user_id=con.ROWID
	inner join campsites cs
		on cs.park=t.park
where
	con.notify=1
	and cs.notify=1
"""

cs='select * from campsites'
td='select * from target_dates'
con='select * from contacts'

sqlite_file='scraper.sqlite3'

def submit_sql_command(QUERY):
	conn=sql.connect(sqlite_file)
	c=conn.cursor()
	c.execute(QUERY)
	conn.commit()
	conn.close()
	return True

def sql_query(QUERY):
	conn=sql.connect(sqlite_file)
	c=conn.cursor()
	c.execute(QUERY)
	array=c.fetchall()
	conn.close()
	return array

def add_user(NAME,EMAIL,NOTIFY,PHONE):
	sql_base="""
		insert into contacts (name,email,notify,phone_number) values('{}','{}',{},{});
	"""
	if NOTIFY:
		NOTIFY=1
	else:
		NOTIFY=0
	submit_sql_command(sql_base.format(NAME,EMAIL,NOTIFY,PHONE))

def update_notification_history(campsite,date,avail_status):
	right_now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	update_sql="INSERT INTO scraper_history (site,availability_date,notification_date,availability) VALUES (\'{}\',\'{}\',\'{}\',{});".format(campsite,date,right_now,avail_status)
	submit_sql_command(update_sql)

def add_target_date(USER_ID,DATE,PARK):
	sql="insert into target_dates (user_id,date,park) values ({},'{}','{}')".format(USER_ID,DATE,PARK)
	submit_sql_command(sql)

def check_notification(campsite,date,avail_status):
	check_avail='select availability from scraper_history where availability_date = \'{}\' and site =\'{}\' order by notification_date desc,availability;'.format(date,campsite)
	results=sql_query(check_avail)
	#print results
	if len(results) == 0: #no results
		val=2
	else:
		val=int(results[0][0])
	if (val != avail_status and val !=2) or (val==2 and avail_status ==1):
		#print "I will notify"
		return True
	else:
		#print "I will not notify"
		return False
def send_email(SUBJECT,MESSAGE,FROM_ADDRESS,TO_ADDRESS):
	headers="\r\n".join(
		[
			'from: ' + creds['gmail']['username'],
			'subject: ' + SUBJECT,
			'to: ' + TO_ADDRESS,
			"mime-version: 1.0",
			"content-type: text/html"
		])
	content = "{}\r\n\r\n{}".format(headers,MESSAGE)
	session = smtplib.SMTP('smtp.gmail.com',587)
	session.ehlo()
	session.starttls()
	session.login(creds['gmail']['username'],creds['gmail']['password'])
	try:
		session.sendmail(creds['gmail']['username'], TO_ADDRESS, content)
	except:
		print('There has been some error sending an email')
	session.quit()

def check_yosemite(URL,DATE,SITE):
	"""Check a site in yosemite for the given day
	navigate to the web page explicitly and then check to see if there is an element """
	target_date=datetime.datetime.strptime(DATE,'%Y-%m-%d').strftime('%-m/%-d/%Y')
	response = br.open(URL.format(target_date))
	html = response.read()
	soup = BeautifulSoup(html)
	sites = soup.findAll('a', attrs={'class':'avail'})
	for site in sites:
		m = re.search('.+arvdate=(' + target_date + ')',str(site.get('href')))
		try:
			if m.group(1) == target_date: 
				#print "found something for {}!".format(site)
				return 1
		except AttributeError:
			pass
	return 0

def send_email_alert(SITE,AVAILABILITY_STATUS,DAY,URL,CONTACTS):
	subject="Status update for {} on {}".format(SITE,DAY)
	if AVAILABILITY_STATUS==1:
		body="""Hi {},
			Looks like site """+SITE+""" is available on """+DAY+""".
			Please see """+URL+""" to reserve.

			Good luck!"""
	else:
		body="""Hi {},
			Site """+SITE+""" is no longer available on """+DAY+""".
			
			Just thought you'd like to know!"""
	for contact in CONTACTS:
		send_email(subject,body.format(contact[0]),'yosemite_updates.gmail.com',contact[1])


# make a scraper class
class SCRAPER():
	def __init__(self):
		self.data={}
	def add_array_element_to_dictionary(self,TUPLE):
		#the date is not in self.data, so I can add it and initialize all the sets etc
		self.data[TUPLE[0]]={ #date
			TUPLE[3]:{        #Park
				TUPLE[1]:{    #site name
					'url':TUPLE[2], #url
					'contact':{(TUPLE[4],TUPLE[5])} #contact info
				}
			}
		}
	def append_information_to_date(self,TUPLE):
		#I know that the date already exists. Add sites, parks, names etc
		park=TUPLE[3]
		target_date=TUPLE[0]
		site=TUPLE[1]
		if park in self.data[target_date]:
			if site in self.data[target_date][park]:
				self.data[target_date][park][site]['contact'].add((TUPLE[4],TUPLE[5]))
			else:
				self.data[target_date][park][site]={'url':TUPLE[2],'contact':{(TUPLE[4],TUPLE[5])}}
		else:
			self.data[target_date][park]={
				site:{
					'url':TUPLE[2],
					'contact':{TUPLE[4],TUPLE[5]}
				}
			}
	def build_data(self):
		#build up data dictionary
		arr=sql_query(dictionary_query)
		for day_tuple in arr:
			if day_tuple[0] not in self.data:
				self.add_array_element_to_dictionary(day_tuple)
			else:
				self.append_information_to_date(day_tuple)
	def check_status(self):
		"""loop through all of the parks camsites and see if there is availability"""
		for day in self.data:
			for site in self.data[day]['Yos']: #I only 
				self.data[day]['Yos'][site]['status']=check_yosemite(self.data[day]['Yos'][site]['url'],day,site)
	def notify_and_update(self):
		for day in self.data:
			for park in self.data[day]:
				for site in self.data[day][park]:
					#print "running notification for site {}".format(site)
					if check_notification(site,day,self.data[day][park][site]['status']):
						update_notification_history(site,day,self.data[day][park][site]['status'])
						send_email_alert(site,self.data[day]['Yos'][site]['status'],day,self.data[day]['Yos'][site]['url'].format(day),self.data[day]['Yos'][site]['contact'])