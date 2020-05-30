from datetime import datetime, timedelta
import mysql.connector
# from django.conf import settings as conf_settings

def expectation(sdate):	
	cnx = mysql.connector.connect(user='admin12', password='admin',
	                              host='localhost',
	                              database='ercess_db'
	                           )

	cursor = cnx.cursor(buffered=True)
	try:
		
		query = "SELECT \
			  articles2.event_name AS event, \
			  expectations_feedbacks.email AS email \
			   FROM articles2  \
	  			INNER JOIN expectations_feedbacks ON articles2.id = expectations_feedbacks.event_id \
  				WHERE articles2.sdate = %s AND expectations_feedbacks.exp_email_attempts < 3 "

		cursor.execute(query, (sdate,))
		record = cursor.fetchall()
		print(record,'=============')
		for row in record:
			emails = row[1]
			print('event_name = ',row[0])
			print('email = ', row[1])

		
		
	except Exception as e:
		raise e
	finally:
		cursor.close()
		cnx.close()

today = datetime.now().date()
tomorrow = today + timedelta(1)

expectation(tomorrow)
