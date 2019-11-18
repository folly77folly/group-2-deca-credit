from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from . import app,db


@app.route("/")
def hello():
    return render_template("index.html")