
s=requests.Session()


s.headers={
'Host': 'www.reserveamerica.com',
'Connection': 'keep-alive',
'Content-Length': 823,
'Cache-Control': 'max-age=0',
'Origin': 'https://www.reserveamerica.com',
'Upgrade-Insecure-Requests': 1,
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Referer': 'https://www.reserveamerica.com/camping/mount-tamalpais-sp/r/campgroundDetails.do?contractCode=CA&parkId=120063',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.8',
'Cookie': """_rauv_=0C8FC7C434D85989F43D051EAA140437.awolvprodweb10_; 
	_rauv_=0C8FC7C434D85989F43D051EAA140437.awolvprodweb10_; 
	__gads=ID=8eba53c7c2e88723:T=1489121560:S=ALNI_Mb8T95bVVbFRNkY2dX3yAVjst-6Bw; 
	OX_plg=swf|shk|pm; GED_PLAYLIST_ACTIVITY=W3sidSI6IlBFL1QiLCJ0c2wiOjE0OTY2MTY1OTAsIm52IjoxLCJ1cHQiOjE0OTY2MTY1ODEsImx0IjoxNDk2NjE2NTkwfV0.; 
	JSESSIONID=6F6EF771E48C80C506A7256A907836B9.awolvprodweb04; 
	utag_main=_st:1496634579641$v_id:015c74c4d00000226c7164c46b3404079006e0710093c$_sn:4$_ss:0$vapi_domain:reserveamerica.com$ses_id:1496632531814%3Bexp-session$_pn:4%3Bexp-session; 
	_ga=GA1.2.221265356.1489028113; 
	_gid=GA1.2.81600991.1496607674; 
	s_cc=true; 
	NSC_MWQSPE-VXQ-IUUQT=ffffffff09d44f0745525d5f4f58455e445a4a422141; 
	s_fid=17D464610C8C0D1C-2B5B5F929D2F6200; 
	s_sq=anreserveamericaprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dreserveamerica%25253Acampground%252520details%2526link%253DSearch%252520Available%2526region%253Denterdates%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dreserveamerica%25253Acampground%252520details%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BUnifSearchEngine.submitForm%252528%252529%25253B%25257D%2526oidt%253D2%2526ot%253DSUBMIT"""
}




data={
'contractCode': 'CA',
'parkId': 120063,
'siteTypeFilter': 'ALL',
'availStatus': None,
'submitSiteForm': 'true',
'search': 'site',
'campingDate': 'Fri Jul 07 2017',
'lengthOfStay': 1,
'campingDateFlex': 'Not Flexible',
'currentMaximumWindow': 12,
'contractDefaultMaxWindow': 'MS:24,LT:18,GA:24,SC:13,PA:24,LARC:24,CTLN:13',
'stateDefaultMaxWindow': 'MS:24,GA:24,SC:13,PA:24,CO:24,CA:13',
'defaultMaximumWindow': 12,
'loop': 'Any Loop',
'siteCode': None,
'lookingFor': 10001,
'camping_2001_3013': '',
'camping_2001_218': None,
'camping_2002_3013': None,
'camping_2002_218': None,
'camping_2003_3012': None,
'camping_3100_3012': None,
'camping_10001_3012': None,
'camping_10001_218': None,
'camping_3101_3012': None,
'camping_3101_218': None,
'camping_9002_3012': None,
'camping_9002_3013': None,
'camping_9002_218': None,
'camping_9001_3012': None,
'camping_9001_218': None,
'camping_3001_3013': None,
'camping_2004_3013': None,
'camping_2004_3012': None,
'camping_3102_3012': None
}


r = s.post(url, data=data)