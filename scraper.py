#!/usr/bin/env python

import re
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import sys
#import mysql.connector
import datetime
import smtplib
from sqlalchemy import *

campsites = [
{"site":"lower pines",
"url":"http://www.recreation.gov/camping/Lower_Pines/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70928&calarvdate={0}"},
{"site":"north pines",
"url":"http://www.recreation.gov/camping/North_Pines/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70927&calarvdate={0}"},
{"site":"upper pines",
"url":"http://www.recreation.gov/camping/Upper_Pines/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70925&calarvdate={0}"},
{"site":"tuolumne meadows",
"url":"http://www.recreation.gov/camping/Tuolumne_Meadows/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70926&calarvdate={0}"},
{"site":"bridaveil creek",
"url":"http://www.recreation.gov/camping/Bridalveil_Creek_Group_And_Horse_Camp/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70931&calarvdate={0}"},
{"site":"hodgdon meadow",
"url":"http://www.recreation.gov/camping/Hodgdon_Meadow/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70929&calarvdate={0}"},
#{"site":"crane flat",
#"url":"http://www.recreation.gov/camping/Crane_Flat/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70930&calarvdate={0}"}
]


cj = cookielib.LWPCookieJar()
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#date_format on site	'4/19/2015'
today=datetime.datetime.today().strftime('%Y-%m-%d')
right_now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    sys.argv[1]
except IndexError:
	start_date=datetime.datetime.today()
else:
	start_date=datetime.datetime.strptime(sys.argv[1],'%Y-%m-%d')

mysql_config={'user':'scraper_logging','password':'*****','host':'localhost','database':'yosemite_scraper_logs'}
engine_string='mysql://{}:{}@localhost/{}?charset=utf8&use_unicode=0'.format(mysql_config['user'],mysql_config['password'],mysql_config['database'])
#create the sqlalchemy engine
engine=create_engine(engine_string,pool_recycle=3600)


#this function will check to see if the availability status of a campsite has changed since the last time I have sent a notification.
#if I find that a site is available (1) then I will check to see if I have already sent a notification of availability
#if avail_status != the previously stored status or if I have never sent a status (only when a site is available) then I will return 1
def check_notification(campsite,date,avail_status):
	check_avail='select availability from scraper_history where availability_date = \'{}\' and site =\'{}\' order by notification_date desc,availability;'.format(date,campsite)
	con=engine.connect()
	results=engine.execute(check_avail)
	arr=[dict(r) for r in results]
	con.close()
	if len(arr) == 0: #no results
		val=2
	else:
		val=arr[0]['availability']
	if (val != avail_status and val !=2) or (val==2 and avail_status ==1):
		return 1
	else:
		return 0



def update_notification_history(campsite,date,avail_status):
	update_sql="INSERT INTO scraper_history (site,availability_date,notification_date,availability) VALUES (\'{}\',\'{}\',\'{}\',{});".format(campsite,date,right_now,avail_status)
	con=engine.connect()
	engine.execute(update_sql)
	con.close()

def find_emails(date):
	email_addresses="select distinct name,email from contacts c inner join target_dates td on td.email_id = c.id where notify=1 and td.date='{}';".format(date)
	con=engine.connect()
	results=engine.execute(email_addresses)
	arr=[dict(r) for r in results]
	return arr
	con.close()

def find_dates():
	dates_query="select distinct date from target_dates;"
	con=engine.connect()
	results=engine.execute(dates_query)
	arr=[dict(r) for r in results]
	return arr 
	con.close()


def send_mails(name,recip,site,avail,date,link):
	fromaddr = '***'
	GMAIL_PASSWORD='****'
	GMAIL_USERNAME='****'
	if avail==1:
		avail_message=" is available "
	else:
		avail_message=" is no longer available "
	email_subject='Yosemite - Status Update for {}'.format(site)
	message='{}{}on {}'.format(site,avail_message,date)
	headers = "\r\n".join(["from: " + GMAIL_USERNAME,
                       "subject: " + email_subject,
                       "to: " + recip,
                       "mime-version: 1.0",
                       "content-type: text/html"])
	if avail==1:
		body='Hi {},\r\n{}.\r\nPlease see\r\n{}\r\nto reserve.\r\n\r\nThanks!'.format(name,message,link)
	else:
		body='HI {},\r\n{}.\r\nJust thought you might like to know!\r\n\r\nThanks!'.format(name,message)
	content = headers + "\r\n\r\n" + body
	session = smtplib.SMTP('smtp.gmail.com', 587)
	session.ehlo()
	session.starttls()
	session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
	try:
		session.sendmail(GMAIL_USERNAME, recip, content)
	except:
		pass
	session.quit()

date_dict=find_dates()
date_arr=[d['date'] for d in date_dict]
for date in (start_date + datetime.timedelta(n) for n in range(30)):
	dt_formatted=date.strftime('%-m/%-d/%Y')
	#if date.weekday() not in [4,5]: #check if it's a friday or saturday - if it's not, then skip to the next date.
	if date.strftime('%Y-%m-%d') not in date_arr:
		continue
	date=date.strftime('%Y-%m-%d')
	emails=find_emails(date)
	print 'checking availability for {}'.format(date)
	for campsite in campsites:
		avl=0
		print 'made it to camp {}'.format(campsite['site'])
		response = br.open(campsite['url'].format(dt_formatted))
		html = response.read()
		soup = BeautifulSoup(html)
		sites = soup.findAll('a', attrs={'class':'avail'})
		for site in sites:
			print 'trying site {}'.format(campsite['site'])
			m = re.search('.+arvdate=(' + dt_formatted + ')',str(site.get('href')))
			try:
				if m.group(1) == dt_formatted: #found a site, now I must see if I have sent an alert for this site recently. Availability of 1 means that a site is available
					avl=1
					break
			except AttributeError:
				avl=0
		#couldn't find any availability should update DB if there was previous avail
		if avl==1:
			print 'there is availability'
		elif avl==0:
			print 'no availability'
		else:
			break
		if check_notification(campsite['site'],date,avl) == 1:
			print '\tthis requires notice'
			for row in emails:
				send_mails(row['name'],row['email'],campsite['site'],avl,date,campsite['url'])
			update_notification_history(campsite['site'],date,avl)
