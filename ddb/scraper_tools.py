import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime

today=datetime.today().strftime('%Y-%m-%d')

class ddb():
    def __init__(self):
        self.ddb = boto3.resource('dynamodb',region_name='us-west-2')

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
            return response['Item']
    
    def query_table(self,table,key,value):
        tb=self.ddb.Table(table)
        response=tb.query(KeyConditionExpression=Key(key).eq(value))
        return response

    def remove_item(self,table,key_expression):
        tb=self.ddb.Table(table)
        response = tb.delete_item(Key=key_expression)
        return response


    def get_target(self,date,park):
        tb=self.ddb.Table('targets')
        response=tb.query(KeyConditionExpression=Key('date').eq(date) & Key('park').eq(park))
        return response['Items']
    
    def scan(self,table):
        tb=self.ddb.Table(table)
        return tb.scan()
    
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

    def add_target(self,park,date,email):
        tb=self.ddb.Table('targets')
        r = self.get_targets(date,park)
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

    def create_table(self,args):
        return self.ddb.create_table(**args)


class ScraperDDB(ddb):
    def __init__(self):
        self.targets=[]
        self.sites_to_notify={}
        self.ddb = boto3.resource('dynamodb',region_name='us-west-2')

    # def get_item(self,table,args):
    #     tb=self.ddb.Table(table)
    #     try:
    #         response = tb.get_item(**args)
    #     except ClientError as e:
    #         print(e.response['Error']['Message'])
    #     else:
    #         return response['Item']

    def post_item(self,table,args):
        tb=self.ddb.Table(table)
        return tb.post_item.get_tem(**args)

    def find_targets(self,park):
        """Find all the parks that need to be scanned.
        Need Sites and then Dates"""
        search_params={'KeyConditionExpression':Key('park').eq(park) & Key('date').gte(today)}
        targets = self.ddb.Table('targets').query(**search_params)
        self.targets = targets['Items']

    def find_sites(self,park):
        """find all sites that need to be scanned"""
        search_params={'KeyConditionExpression':Key('park').eq(park) & Key('date').gte(today)}
        targets = self.ddb.Table('targets').query(**search_params)
        self.targets = targets['Items']

    def check_update_status(self,date,park,site):
        args = {
            "Key":{
                'date':date,
                'park_site':park + '-' + site
            }
        }
        return self.get_item('notifications',**args)

    def check_notify_update(self,date,park,site,available,user_list):
        """first get the update status of the park 
        then decide what to do
        then update the status based on what you do"""
        args = {
            "Key":{
                'date':date,
                'park_site':park + '-' + site
            }
        }
        user_map = self.get_item(**args)['user_status']
        self.notify(date,park,site,available,user_list,user_map)
        new_map = {user:available for user in user_list}
        user_map.update(new_map)
        args['user_status'] = user_map
        self.put_item(**args)

    def notify(self,date,park,site,available,user_list,user_map):
        for user in  user_list:
            self.send_email(user,date,park,site,available)



