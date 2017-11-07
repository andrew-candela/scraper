import requests
import re
from BeautifulSoup import BeautifulSoup
from datetime import datetime



s=requests.Session()
s.headers={
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
}
upper_pines_url = 'http://www.recreation.gov/camping/Upper_Pines/r/campsiteCalendar.do?page=calendar&search=site&contractCode=NRSO&parkId=70925&calarvdate={}'


def check_yosemite(URL,DATE):
	"""Check a site in yosemite for the given day
	navigate to the web page explicitly and then check to see if there is an element """
	target_date=datetime.strptime(DATE,'%Y-%m-%d').strftime('%-m/%-d/%Y')
	search_string='.+arvdate=(' + target_date + ')'
	reg_exp=re.compile(search_string)
	response = s.get(URL.format(target_date),verify=False)
	html = response.text
	soup = BeautifulSoup(html)
	sites = soup.findAll('a', attrs={'class':'avail'})
	for site in sites:
		m = reg_exp.search(str(site.get('href')))
		try:
			if m.group(1) == target_date:
				#print "found something for {}!".format(site)
				return True
		except AttributeError:
			pass
	return False