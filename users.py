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
        row = db.execute(f"Select * from users where email='{email}'")
        session["user_id"] = row[0]["id"]
        session["user_email"] = row[0]["email"]
        return redirect("/userdashboard")
# @app.route('/login.html')
# def login():
#     return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login_post():
    if request.method=="GET":
        return render_template("login.html")
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
        return redirect("/userdashboard")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    """User apply"""
    if request.method=='GET':
        return render_template("apply.html")
    if request.method=='POST':
        amount=int(request.form.get("amount"))
        tenor=request.form.get("tenor")
        email = session["user_email"]
        user_id = session["user_id"]
        balance = -(amount)
        interest = amount * (10 / 100)
        installment = (amount + interest) / tenor

        if not amount or not tenor:
            return apology("please provide amount and tenor")
        if amount < 5000:
            return apology("yu cannot borrow less than 5000")
        user = db.execute(f"SELECT * FROM users WHERE email= {email}")
        if user[0]["bvn"] == None:
            return redirect("editprofile.html")
        elif user[0]["cbalance"] < 0:
            return apology("please pay up your outstanding loan")
        else:
            db.execute(f"INSERT INTO loans (user_id, amount, status, tenor, installment, balance, repaid) VALUE('{user_id}', '{amount}', 'pending', '{tenor}', '{installment}', '{balance}', 0)")
        row = db.execute(f"SELECT * FROM loans WHERE user_id= {user_id}")
        return render_template("userdashboard.html", row)
