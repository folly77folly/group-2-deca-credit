from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from . import app,db
from .helpers import apology


@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/register.html", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method=='GET':
        return render_template("register.html")
    if request.method=='POST':
        email=request.form.get("email")
        passw=request.form.get("password")
        cpassw=request.form.get("confirmpassword")
        user_name=db.execute(f"Select email from users where email='{email}'")
        if user_name:
            message="email Already Taken"
            return apology(message)
        if email=="" or passw=="" or cpassw=="":
            message="email or Password or Confrim Password Cannot be Empty"
            return apology("message")
        if passw!=cpassw:
            message="Password Mismatch"
            return apology(message)
            # Query database for email
        passhash=generate_password_hash(passw)
        role=0
        # db.execute(f"insert into users(email,pass_word) values({email},{passhash})")
        db.execute(f"insert into users(email,pass_word,role) values('{email}','{passhash}','{role}')")
        row = db.execute(f"Select email from users where email='{email}'")
        print(row)
        return redirect("/userdashboard")
# @app.route('/login.html')
# def login():
#     return render_template('login.html')

@app.route('/login.html', methods=['POST', 'GET'])

def login_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
        
        if len(user):
            if check_password_hash(user[0]["pass_word"], password):
                session['user_id'] = user[0]['id']
                session['user_email'] = user[0]['email']
                return redirect('/')
            else:
                return apology("invalid email or password")
        else:
            return apology("invalid email or password")
    else:
        return render_template('login.html')