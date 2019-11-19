from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from . import app,db



@app.route('/request')
def pending():
    status = "pending"
    pending = db.execute(f"SELECT * FROM loan WHERE status = '{status}'")
    return render_template("request.html", pending=pending)
