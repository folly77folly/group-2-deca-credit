from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from . import app,db

@app.route("/outstanding")
def apply():
    """admin view oustanding loan"""
    status = "active"
    repaid = 0
    outstanding = db.execute(f"SELECT * FROM loans WHERE status = '{status}' AND repaid = '{repaid}'")
    return render_template("outstanding.html", oustanding = outstanding)