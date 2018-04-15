#! /usr/bin/env python3.5
# -*- coding:utf-8 -*-
import time,requests,datetime
import sqlite3
conn = sqlite3.connect('projet.db')

cursor = conn.cursor()
while True:
	time.sleep(5)
	cursor.execute('SELECT url,id FROM sites')
	listes = cursor.fetchall()
	date_now = datetime.datetime.now()
	for row in listes:
		statut = requests.get(row[0])
		cursor.execute("INSERT INTO log (id_site,date,result_request) VALUES ("+str(row[1])+",'"+str(date_now)+"',"+str(statut.status_code)+");")
		conn.commit()
		continue
	print('Insertion dans la base de données terminée')