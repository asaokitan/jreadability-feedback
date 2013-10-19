#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os, sys
import jreadability_feedback as jf
import unittest
import tempfile

import json

class AppTestCase(unittest.TestCase):
        
	def setUp(self):
		self.db_fd, jf.app.config['DATABASE'] = tempfile.mkstemp()
		jf.app.config['TESTING'] = True
		self.app = jf.app.test_client()
		jf.init_db()
	
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(jf.app.config['DATABASE'])

	def login(self, username, password):
	    return self.app.post('/login', data=dict(
	        username=username,
	        password=password
	    ), follow_redirects=True)

	def logout(self):
	    return self.app.get('/logout', follow_redirects=True)

	def view(self):
		return self.app.get('/view', follow_redirects=True)

	def test_login(self):
		rv = self.app.get('/login')
		assert u'ユーザ名' in rv.data.decode('utf-8')

	def test_empty_db(self):
		rv = self.login('admin', 'default')
		rv = self.app.get('/view')
		assert u'ありません' in rv.data.decode('utf-8')

	def test_login_logout(self):
	    rv = self.login('admin', 'default')
	    assert u'ログイン' in rv.data.decode('utf-8')
	    rv = self.logout()
	    assert u'ログアウト' in rv.data.decode('utf-8')
	    rv = self.login('adminx', 'default')
	    assert u'無効です' in rv.data.decode('utf-8')
	    rv = self.login('admin', 'defaultx')
	    assert u'無効です' in rv.data.decode('utf-8')
    
	def test_messages(self):
		self.login('admin', 'default')
		rv = self.app.post('/post', data=json.dumps(dict(
				original_text=u'ものは試し',
				evaluation=5,
				grade=4,
		)), follow_redirects=True)
		assert rv.status_code == 204
		rv = self.view()
		assert u'ありません' not in rv.data.decode('utf-8')
		assert u'ものは試し' in rv.data.decode('utf-8')

if __name__ == '__main__':
	unittest.main()
