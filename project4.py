import praw
import json
import sqlite3
import datetime
import googlemaps
from datetime import date
from datetime import datetime
import calendar
from coinbase.wallet.client import Client
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

#Cache setup
reddit_cache = "reddit_cache.json"
try:
    cache_file = open(reddit_cache,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    REDDIT_CACHE_DICTION = json.loads(cache_contents)
except:
    REDDIT_CACHE_DICTION = {}


coinbase_cache = "coinbase_cache.json"
try:
    cache_file = open(coinbase_cache,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    COINBASE_CACHE_DICTION = json.loads(cache_contents)
except:
    COINBASE_CACHE_DICTION = {}

gmaps_cache = "gmaps_cache.json"
try:
    cache_file = open(gmaps_cache,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    GMAPS_CACHE_DICTION = json.loads(cache_contents)
except:
    GMAPS_CACHE_DICTION = {}

reddit = praw.Reddit(client_id='2zxewSoLd8wqZw',
                     client_secret='76xV_JAPH-o0YpGaHrA7N2i_pDQ',
                     user_agent='my user agent',
                     username='SI206',
                     password='umsi206')

#getReddit function: Pulls top 100 posts from a reddit ssubreddit. Stores the post id, 
#title, author, score, day posted, and time posted. Cache organized by subreddit.
def getReddit(sub):
	if sub in REDDIT_CACHE_DICTION:
		print("Data was in the reddit cache")
		return REDDIT_CACHE_DICTION[sub]
	else:
		print("Making a request for new data from reddit...")
		subreddit = reddit.subreddit(sub)
		data = subreddit.top(limit=100)
		l = []
		for post in data:
			post_time = datetime.fromtimestamp(post.created)
			day = calendar.day_name[post_time.weekday()]
			tup = post.id, post.title, str(post.author), post.score, day, post_time
			d = {}
			d['id'] = str(tup[0])
			d['title'] = str(tup[1])
			d['author'] = str(tup[2])
			d['score'] = str(tup[3])
			d['day'] = str(tup[4])
			d['post_time'] = str(tup[5])
			l.append(d)

		REDDIT_CACHE_DICTION[sub] =  l
		dumped_json_cache = json.dumps(REDDIT_CACHE_DICTION)

		fw = open(reddit_cache,"w")
		fw.write(dumped_json_cache)
		fw.close() # Close the open file
		return REDDIT_CACHE_DICTION[sub]

#Calls getReddit on reddit.com/r/all
reddit_all = getReddit('all')

conn = sqlite3.connect('206_final.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Reddit')
cur.execute('CREATE TABLE Reddit (post_id TEXT, title TEXT, user TEXT, score NUMBER, day_posted TEXT, time_posted TEXT)')

for post in reddit_all:
	tup = post['id'], post['title'], post['author'], post['score'], post['day'], post['post_time']
	cur.execute('INSERT INTO Reddit (post_id, title, user, score, day_posted, time_posted) VALUES (?, ?, ?, ?, ?, ?)', tup)
conn.commit()

reddit_dict = {}
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in days:
	reddit_dict[day] = 0

for post in reddit_all:
	for x in days:
		if post['day'] == x:
			reddit_dict[x] += 1

objects = ( 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
y_pos = np.arange(len(objects))
num_posts = []
for x in objects:
	num_posts.append(reddit_dict[x]) 
plt.bar(y_pos, num_posts, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Posts')
plt.title('Top Reddit Posts By Day')
 
plt.show()

client = Client('e3a823a3ecf0641ea4a24782c00ac4b72bc6e2927b9d2819d651bf8190a13168', '8a7bb48ad83394ffc31701c0387a5e3f53f6f19981cb2f6d5495adf28c55ac9c')

def getCoinbase(day):
	if day in COINBASE_CACHE_DICTION:
		print("Data was in the coinbase cache")
		return COINBASE_CACHE_DICTION[day]

	else:
		print("Making a request for new data from coinbase...")
		prices = client.get_historic_prices()
		l = []
		for price in prices['prices']:
			d = {}
			tup = price['time'], price['price']
			d['time'] = tup[0]
			d['price'] = tup[1]
			l.append(d)

		COINBASE_CACHE_DICTION[day] =  l
		dumped_json_cache = json.dumps(COINBASE_CACHE_DICTION)

		fw = open(coinbase_cache,"w")
		fw.write(dumped_json_cache)
		fw.close() # Close the open file
		return COINBASE_CACHE_DICTION[day]

day = datetime(2017, 12, 1, 0, 0, 0, 0)
day = str(day)
coinbase = getCoinbase(day)

cur.execute('DROP TABLE IF EXISTS Coinbase')
cur.execute('CREATE TABLE Coinbase (date TEXT, price NUMBER)')

for price in coinbase:
	tup = price['time'], price['price']
	cur.execute('INSERT INTO Coinbase (date, price) VALUES (?, ?)', tup)
conn.commit()

cur.execute('DROP TABLE IF EXISTS Maps')
cur.execute('CREATE TABLE Maps (time TIMESTAMP, duration NUMBER)')



gmaps = googlemaps.Client(key='AIzaSyBualpHzVrPZdwM_sHDO-d4iQEd9b-UJcA')

def getGmaps(day):
	if day in GMAPS_CACHE_DICTION:
		print("Data was in the google maps cache")
		return GMAPS_CACHE_DICTION[day]

	else:
		print("Making a request for new data from google maps...")
		t = datetime(2017, 12, 1, 6, 0, 0, 0)
		l = []
		while t.day < 8:
			directions_result = gmaps.directions("Angel Hall, Ann Arbor",
    		                                 	"Michigan Stadium",
            		                         	mode="transit",    
 	  		        		                  	departure_time=t) 

			duration = directions_result[0]['legs'][0]['duration']['text']
			duration = int(duration.split()[0])
			d = {}
			d['time'] = str(t)
			d['duration'] = duration
			l.append(d)

			if t.hour == 20:
				t = t.replace(hour = 6)
				t = t.replace(day = t.day + 1)
			else:
				t = t.replace(hour = t.hour + 1)

		GMAPS_CACHE_DICTION[day] = l
		dumped_json_cache = json.dumps(GMAPS_CACHE_DICTION)

		fw = open(gmaps_cache,"w")
		fw.write(dumped_json_cache)
		fw.close() # Close the open file
		return GMAPS_CACHE_DICTION[day]

day = datetime(2017, 12, 1, 0, 0, 0, 0)
day = str(day)
gmaps = getGmaps(day)
for hour in gmaps:
	tup = hour['time'], hour['duration']
	cur.execute('INSERT INTO Maps (time, duration) VALUES (?, ?)', tup)

conn.commit()


