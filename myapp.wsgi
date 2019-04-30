#!/usr/bin/python
from project import app
from flask import Flask

app.debug = True
app.secret_key = 'super_secret_key'
app.run(host='0.0.0.0', port=5000)
