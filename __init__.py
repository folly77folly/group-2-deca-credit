from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
# from flask_session import Session
# from tempfile import mkdtemp
from flask_mail import Mail, Message
from . import send_mail

app = Flask(__name__)

mail=Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# app.config['MAIL_SERVER']="smtp.sendgrid.net"
# app.config['MAIL_PORT']='465'
# app.config['MAIL_USE_TLS']=False
# app.config['MAIL_USE_SSL']=True
# app.config['MAIL_USERNAME']="apikey"
# app.config['MAIL_PASSWORD']="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"
# # app.config['MAIL_DEFAULT_SENDER']="test email"
# app.config['MAIL_ASCII_ATTACHEMENTS']=True
# # app.config['SECRET_KEY'] = '8989'


# app.config['MAIL_SERVER']="smtp.gmail.com"
# app.config['MAIL_PORT']='465'
# app.config['MAIL_USE_TLS']=False
# app.config['MAIL_USE_SSL']=True
# app.config['MAIL_USERNAME']="iamaqim@gmail.com"
# app.config['MAIL_PASSWORD']="omogbolahan417"
# app.config['MAIL_DEFAULT_SENDER']="test email"
# app.config['MAIL_ASCII_ATTACHEMENTS']=True
app.config['SECRET_KEY'] = '8985435345359'



# Ensure responses aren't cached
# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# # Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///credit.db")

from . import users,admin
