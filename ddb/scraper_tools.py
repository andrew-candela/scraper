import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime
from email_sender import *
from web_scraper import *


today=datetime.today().strftime('%Y-%m-%d')
now=datetime.now().strftime('%Y-%m-%d:%H:%M:%S')

class DDB():
    
    ddb = boto3.resource('dynamodb',region_name='us-west-2')
    db_client = boto3.client('dynamodb',region_name='us-west-2')

    def post_item(self,table,args):
        tb=self.ddb.Table(table)
        return tb.put_item(**args)
    
    def get_item(self,table,args):
        tb=self.ddb.Table(table)
        try:
            response = tb.get_item(**args)
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response
    
    def query_table(self,table,key,value):
        tb=self.ddb.Table(table)
        response=tb.query(KeyConditionExpression=Key(key).eq(value))
        return response

    def remove_item(self,table,key_expression):
        tb=self.ddb.Table(table)
        response = tb.delete_item(Key=key_expression)
        return response
    
    def scan(self,table):
        tb=self.ddb.Table(table)
        return tb.scan()
    
    def create_table(self,args):
        return self.ddb.create_table(**args)

class LoadData(DDB):
    def load_contacts(self,contacts_array):
        for con in contacts_array:
            args={
                'Item':{
                    'name':con[0],
                    'email':con[1],
                    'phone':con[3],
                    'notify':bool(con[2])
                }
            }
            self.post_item('contacts',args)
    
    def load_campsites(self,campsites_array):
        for camp in campsites_array:
            args={
                'Item':{
                    'site':camp[0],
                    'url':camp[1],
                    'park':camp[2],
                    'notify':bool(camp[3])
                }
            }
            self.post_item('campsites',args)
        print "loaded some campsites into the campsites table"

class ScraperDDB(DDB,Email):

    targets=[]
    # self.ddb = boto3.resource('dynamodb',region_name='us-west-2')
    # self.db_client = boto3.client('dynamodb',region_name='us-west-2')

    def find_targets(self,park):
        """Find all the parks that need to be scanned.
        Need Sites and then Dates"""
        search_params={'KeyConditionExpression':Key('park').eq(park) & Key('date').gte(today)}
        targets = self.ddb.Table('targets').query(**search_params)
        self.targets = targets['Items']

    def get_target(self,date,park):
        #used for add_target - when adding a user to the target date
        tb=self.ddb.Table('targets')
        response=tb.query(KeyConditionExpression=Key('date').eq(date) & Key('park').eq(park))
        return response

    def clear_targets(self,park,date):
        r = self.db_client.delete_item(
            TableName = 'targets',
            Key = {
                'park':{'S':park},
                'date':{'S':date}
            }
        )
        return r

    def add_target(self,park,date,email):
        tb=self.ddb.Table('targets')
        r = self.get_target(date,park)
        if type(email) == str:
            email = [email]
        if r['Count'] > 0:
            user_set=r['Items'][0]['emails']
        else:
            user_set=set()
        for em in email:
            user_set.add(em)
        print user_set
        args={
            'Item':{
                'park':park,
                'date':date,
                'emails':user_set
            }
        }
        return tb.put_item(**args)

    def get_user_data(self,email):
        args={
            'Key':{
                'email':email
            }
        }
        return self.get_item('contacts',args).get('Item',None)

    def find_sites_from_park(self):
        parks=set()
        self.parks={}
        for target in self.targets:
            parks.add(target['park'])
        for park in parks:
            search_params={'KeyConditionExpression':Key('park').eq(park)}
            sites=self.ddb.Table('campsites').query(**search_params)
            if sites['Count'] > 0:
                self.parks[park]=sites['Items']

    def check_availability(self):
        for target in self.targets:
            if target['park'] == 'Yosemite':
                for site in self.parks['Yosemite']:
                    if site['notify']:
                        print "{}: checking availability for {}".format(now,site['site'])
                        site['availability'] = check_yosemite(site['url'],target['date'])
            else:
                print "I don't know how to search for sites in {}".format(target['park'])


    #need to decide how to notify
    #for each park, look at the update status

    def check_update_status(self):
        for target in self.targets:
            for site in self.parks[target['park']]:
                args = {
                    "Key":{
                        'park_site':target['park'] + '-' + site['site'],
                        'date':target['date']
                    }
                }
                avail = self.get_item('notifications',args).get('Item',None)
                if avail:
                    site['last_available_status']=avail['available']
                else:
                    site['last_available_status']=False

    def notify(self,user,status,park,site_name,date,url):
        user_info=self.get_user_data(user)
        if not user_info:
            return None
        if status:
            message = """Hello {user}!\n\nLooks like {site} in {park} is available on {date}\n. Please see\n{url}\nto book.
            \n\nThanks!\n-The Scraper""".format(user=user_info['name'], site=site_name, url=url, date=date, park=park)
            subject = """{} Available {}""".format(site_name,date)
        else:
            message = """Hello {user},\n\nLooks like {site} in {park} is no longer available.
            Just thought you would like to know.
            Thanks,
            -The Scraper""".format(user=user, site=site_name, park=park)
            subject = """{} NO Longer Available {}""".format(site_name,date)
        self.send_message([user],subject,message)

    def update_notifications(self,park,site,date,availability,user_array):
        args = {
            "Item":{
                'park_site':park + '-' + site,
                'last_notified':now,
                'available':availability,
                'user_array':user_array,
                'date':date
            }
        }
        r = self.post_item('notifications',args)
        return r

    def notify_and_update(self):
        """look through self.parks and see which sites need to be notified
        once email notification happens, update notification status"""
        for target in self.targets:
            for site in self.parks[target['park']]:
                if site['availability'] != site['last_available_status']:
                    for user in target['emails']:
                        self.notify(user,site['availability'],site['park'],site['site'],target['date'],site['url'])
                    self.update_notifications(site['park'],site['site'],target['date'],site['availability'],target['emails'])

    def run_notification(self,park):
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"finding targets")
        self.find_targets(park)
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"finding sites")
        self.find_sites_from_park()
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"checking availability")
        self.check_availability()
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"checking update status")
        self.check_update_status()
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"sending emails")
        self.notify_and_update()
        print "{}: {}".format(datetime.now().strftime('%Y-%m-%d:%H:%M:%S'),"done")

