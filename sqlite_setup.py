import sqlite3
import pandas as pd 
#create the database that I will use

scraper_history_create="""create table scraper_history (
	availability_date date,
	site varchar(250),
	notification_date date,
	availability varchar(50))
"""
contacts_create="""create table contacts (
	name varchar(100),
	email varchar(250),
	notify int,
	phone_number int
	)
"""
target_dates_create="""create table target_dates(
	user_id int,
	date date,
	park varchar(100))"""

campsites_create="""create table campsites (
	site varchar(100),
	url varchar(500),
	park varchar(100),
	notify int
)"""

sqlite_file = 'scraper.sqlite3'
table_name1 = 'scraper_history'
table_name2 = 'contacts'


# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# create the tables
for sql in [scraper_history_create,contacts_create,target_dates_create,campsites_create]:
	c.execute(sql)

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()


#load data into database with pandas
conn=sqlite3.connect(sqlite_file)
for filename,table in [('websites.csv','campsites'),('contacts.csv','contacts'),('target_dates.csv','target_dates')]:
	df=pd.read_csv(filename)
	df.to_sql(table,conn,if_exists='append', index=False)
conn.commit()
conn.close()

