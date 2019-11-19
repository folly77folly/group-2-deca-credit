from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from . import app,db
from .helpers import apology
from .api import callbanks

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    error = None
    if request.method=='POST':
        email=request.form.get("email")
        passw=request.form.get("password")
        cpassw=request.form.get("confirmpassword")
        user_name=db.execute(f"Select email from users where email='{email}'")
        if user_name:
            error = "email Already Taken"
            return render_template("register.html", error = error)
        if email=="" or passw=="" or cpassw=="":
            error="email or Password or Confrim Password Cannot be Empty"
            return render_template("register.html", error = error)

        if passw!=cpassw:
            error="Password Mismatch"
            return render_template("register.html", error = error)

            # Query database for email
        passhash=generate_password_hash(passw)
        role=0
        # db.execute(f"insert into users(email,pass_word) values({email},{passhash})")
        db.execute(f"insert into users(email,pass_word,role) values('{email}','{passhash}','{role}')")
        row = db.execute(f"Select email from users where email='{email}'")
        row = db.execute(f"Select * from users where email='{email}'")
        session["user_id"] = row[0]["id"]
        session["user_email"] = row[0]["email"]
        flash('You were successfully logged in')
        return redirect("dashboard.html",email= session["user_email"] )
    return render_template("register.html")
# @app.route('/login.html')
# def login():
#     return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login_post():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
        
        if len(user):
            if check_password_hash(user[0]["pass_word"], password):
                session['user_id'] = user[0]['id']
                session['user_email'] = user[0]['email']
                return render_template('dashboard.html', email= session["user_email"])
            else:
                error = "invalid email or password"
                return render_template("register.html", error = error)
        else:
            error = "invalid email or password"
            return render_template("register.html", error = error)
        if user[0]["role"] == 1:
            return redirect("admin.html", email= session["user_email"])
        else:
            return redirect("dashboard.html", email= session["user_email"])
    return render_template("login.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    """User apply"""
    error = None
    if request.method=='POST':
        user_id = session["user_id"]
        user_balance = db.execute(f"SELECT * FROM users WHERE id= '{user_id}'")
        balance = user_balance[0]["cbalance"]
        if not request.form.get("amount") or not request.form.get("tenor"):
            error = "please provide amount and tenor"
            return render_template("apply.html", error = error)
        amount=int(request.form.get("amount"))
        tenor=int(request.form.get("tenor"))
        email = session["user_email"]
        interest = amount * (10 / 100)
        installment = (amount + interest) / tenor
        if amount < 5000:
            error = "you cannot borrow less than 5000"
            return render_template("apply.html", error = error)
        user = db.execute(f"SELECT * FROM users WHERE email= '{email}'")
        if user[0]["bvn"] == None:
            flash("please update your profile")
            return redirect("/edit")
        elif user[0]["cbalance"] < 0:
            error = "please pay up your outstanding loan"
            return render_template("apply.html", error = error)
        else:
            db.execute(f"INSERT INTO loans (user_id, amount, status, tenor, installment, balance, repaid) VALUE('{user_id}', '{amount}', 'pending', '{tenor}', '{installment}', '{balance}', 0)")
        row = db.execute(f"SELECT * FROM loans WHERE user_id= '{user_id}'")
        return render_template("dashboard.html", row = row)
    return render_template("apply.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/edit", methods=["GET", "POST"])
def edit_profile():
    """Edit  user Profile"""
    #check for session
    sess_id=session["user_id"]
    if not check_session(sess_id):
        return redirect("/")
    if request.method=='GET':
        rows = db.execute(f"select * from users where id = '{sess_id}'")
        lsofbanks=callbanks()
        if lsofbanks:
            return render_template("editprofile.html",details=rows,banks=lsofbanks, email= session["user_email"] )
        return render_template("editprofile.html",details=rows, email= session["user_email"])
    if request.method=='POST':
        acctno=request.form.get("acctno").strip()
        bvn=request.form.get("bvn").strip()
        cbalance=request.form.get("cbalance").strip()

        first_name=request.form.get("first_name").strip()
        last_name=request.form.get("last_name").strip()
        phone=request.form.get("phone").strip()
        bank_name=request.form.get("bank_name").strip()

        identification=request.form.get("identification").strip()
        address=request.form.get("address").strip()
        nxtofkin=request.form.get("nxtofkin").strip()

        nxtofkin_phone=request.form.get("nxtofkin_phone").strip()

        if not acctno or not bvn:
            message="You Must Fill your Account Number and BVN Details"
            return apology(message)
        rows=db.execute(f"Update users set acctno='{acctno}', bvn='{bvn}',first_name='{first_name}',last_name='{last_name}',\
                phone='{phone}',bank_name='{bank_name}', identification='{identification}',address='{address}',nxtofkin='{nxtofkin}',\
                nxtofkin_phone='{nxtofkin_phone}' where id='{sess_id}'")
        flash("User Records Updated")
        return redirect("dashboard.html", email= session["user_email"])

def check_session(sess_id):
    user_id=sess_id
    rusers=db.execute(f"select * from users where id ='{user_id}'")
    if rusers:
        return True
    else:
        return False
