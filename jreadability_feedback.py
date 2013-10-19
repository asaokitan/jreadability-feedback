#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
		abort, render_template, flash
from contextlib import closing
import json

# config (will be overridden by setting file)
DATABASE = 'db/jreadability_feedback.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FEEDBACK_SETTINGS', silent=True)

fields = ['id', 'evaluation', 'ip_address', 'original_text',
		'readability', 'grade', 'timedate',
		'avg_num_of_words', 'kango', 'wago', 'doushi', 'joshi']
fieldsj = ['ID', u'ユーザ評価値', u'IPアドレス', u'原文',
		u'リーダビリティ値', u'リーダビリティ級', u'送信日時',
		u'平均文長', u'漢語率', u'和語率', u'動詞率', u'助詞率']

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()
@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def home():
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	else:
		return redirect(url_for('view'))

@app.route('/view')
def view():
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	cur = g.db.execute('select * from posts order by id desc')
	posts = cur.fetchall()
	return render_template('view.html', posts=posts, fieldsj=fieldsj)

@app.route('/post', methods=['POST'])
def post():
	feedback_post = json.loads(request.data)
	
	query = 'insert into posts (%s) values (%s)' % \
			(','.join(fields), ','.join(['?'] * len(fields)))
	g.db.execute(query, [feedback_post.get(field) for field in fields])
	g.db.commit()
	return '', 204

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = u'ユーザ名またはパスワードが無効です'
		elif request.form['password'] != app.config['PASSWORD']:
			error = u'ユーザ名またはパスワードが無効です'
		else:
			session['logged_in'] = True
			# flash(u'ログインしました')
			return redirect(url_for('view'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash(u'ログアウトしました')
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run()
