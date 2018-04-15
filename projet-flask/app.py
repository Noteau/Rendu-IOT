#! /usr/bin/env python3.5
# -*- coding:utf-8 -*-
import requests, sqlite3,datetime,re

from flask import Flask, request, render_template, redirect, url_for,session,flash
from functools import wraps
app = Flask(__name__)
app.secret_key = 'aqwzsxedc'
con = sqlite3.connect('projet.db')


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index () :
		try:
			#recuperation données sql
			cur = con.cursor()
			cur.execute('SELECT Count(*) FROM sites')
			length = [row[0] for row in cur.fetchall()]
			cur.execute("SELECT url, result_request, id FROM sites INNER JOIN log ON id_site = id ORDER BY date DESC LIMIT "+str(length[0])+";")
			liste = cur.fetchall()
			return render_template('index.html',liste = liste)
		except Exception as e:
			return render_template('index.html')

@app.route('/connexion', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Vous vous etes trompe de login/mot de passe.'
        else:
        	session['logged_in'] = True
        	return redirect(url_for('admin'))
    if 'logged_in' in session:
    	return redirect(url_for('admin'))
    return render_template('connexion.html', error=error)

@app.route('/admin')
@login_required
def admin():
	cur = con.cursor()
	cur.execute('SELECT id,url FROM sites ORDER BY id;')
	sites = cur.fetchall()
	return render_template('admin.html',sites=sites)

@app.route('/admin/add', methods = ['GET','POST'])
@login_required
def admin_add():
	error = ''
	if request.method == 'POST':
		error = "Votre Url est vide"
		if request.form['url'] != '':
			urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',str(request.form['url']))
			print(urls)
			if urls :
				cur = con.cursor()
				cur.execute("INSERT INTO sites (url) VALUES ('"+str(request.form['url'])+"');")
				cur.execute("SELECT id FROM sites WHERE url = '"+str(request.form['url'])+"' LIMIT 1")
				id = [row[0] for row in cur.fetchall()]
				date_now = datetime.datetime.now()
				statut = requests.get(request.form['url'])
				cur.execute("INSERT INTO log(id_site,date,result_request) VALUES ("+str(id[0])+",'"+str(date_now)+"',"+str(statut.status_code)+");")
				con.commit()
				cur = con.cursor()
				cur.execute('SELECT id,url FROM sites ORDER BY id;')
				sites = cur.fetchall()
				return render_template('admin.html',sites=sites)
			error = "Votre Url n'est pas valide"
	return render_template('admin_add.html',error=error)

@app.route('/admin/modifier/<choix>', methods = ['GET','POST'])
@login_required
def admin_modifier(choix):
	cur=con.cursor()
	cur.execute("SELECT url FROM sites WHERE id="+str(choix))
	site = [row[0] for row in cur.fetchall()]
	error = ''
	if request.method == 'POST':
		error = "Votre Url est vide"
		if request.form['url'] != '':
			urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',str(request.form['url']))
			print(urls)
			if urls :
				cur = con.cursor()
				cur.execute("UPDATE sites SET url= '"+str(request.form['url']+"' WHERE id="+str(choix)))
				con.commit()
				cur = con.cursor()
				cur.execute('SELECT id,url FROM sites ORDER BY id;')
				sites = cur.fetchall()
				return render_template('admin.html',sites=sites)
			error = "Votre Url n'est pas valide"
		return render_template('admin_modifier.html',error=error,site=site,choix=choix)
	return render_template('admin_modifier.html',site=site, choix=choix)


@app.route('/admin/destroy/<choix>', methods = ['GET','POST'])
@login_required
def admin_destroy(choix):
	cur=con.cursor()
	cur.execute("DELETE FROM sites WHERE id="+str(choix))
	error = ''
	cur=con.cursor()
	cur.execute("SELECT url FROM sites ORDER BY id;")
	site = [row[0] for row in cur.fetchall()]
	return redirect(url_for('index'))


@app.route('/admin/supprimer/<choix>', methods = ['GET','POST'])
@login_required
def admin_supprimer(choix):
	cur=con.cursor()
	cur.execute("SELECT url FROM sites WHERE id="+str(choix))
	site = [row[0] for row in cur.fetchall()]
	error = ''
	return render_template('admin_delete.html',site=site, choix=choix)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/statut')
def statut() :
	try:		
		statut = requests.get(site)
		return render_template('statut.html', r= r)
	except Exception as e:
		return render_template('statut.html', r=520)
	
@app.route('/fiche/<choix>')
def fiche(choix):
	cur = con.cursor()
	cur.execute("SELECT url, result_request , date FROM sites INNER JOIN log ON id_site = id WHERE id = "+choix+" ORDER BY date DESC")
	logs = cur.fetchall()
	return render_template('fiche.html',logs=logs)
	


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')