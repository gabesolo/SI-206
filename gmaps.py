import praw
import json
import sqlite3
import datetime
import googlemaps
from datetime import date
from datetime import datetime
import calendar
from coinbase.wallet.client import Client


gmaps = googlemaps.Client(key='AIzaSyBualpHzVrPZdwM_sHDO-d4iQEd9b-UJcA')
eta_dict = {}
t = datetime(2017, 12, 1, 0, 0, 0, 0)
while t.day < 8:
	directions_result = gmaps.directions("Angel Hall, Ann Arbor",
                                     	"Michigan Stadium",
                                     	mode="transit",    
 	  		                          	departure_time=t) 

	tup = t, directions_result[0]['legs'][0]['duration']['text']

	if t.minute == 30:
		t = t.replace(minute = 0)

		if t.hour == 19:
			t = t.replace(hour = 6)
			t = t.replace(day = t.day + 1)
		else:
			t = t.replace(hour = t.hour + 1)

	else:
		t = t.replace(minute = t.minute + 30)