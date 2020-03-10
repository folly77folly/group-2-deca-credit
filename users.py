from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json,url_for,abort,session
# from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
# from . import app,db
# from .helpers import apology, send_mail,naira
# from .api import callbanks, verifybvn
import app,db
import apology, send_mail,naira
import callbanks, verifybvn

import string
import requests
import random

@app.route("/")
def home():
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
        if len(passw)<=5:
            error="Password cannot be less than 6 characters"
            return render_template("register.html", error = error)

        if passw!=cpassw:
            error="Password Mismatch"
            return render_template("register.html", error = error)

            # Query database for email
        passhash=generate_password_hash(passw)
        role=0
        active='Y'
        # db.execute(f"insert into users(email,pass_word) values({email},{passhash})")
        db.execute(f"insert into users(email,pass_word,role,active) values('{email}','{passhash}','{role}','{active}')")
        row = db.execute(f"Select email from users where email='{email}'")
        row = db.execute(f"Select * from users where email='{email}'")
        session["user_id"] = row[0]["id"]
        session["user_email"] = row[0]["email"]
        flash('Welcome, Update your Profile to Continue!')
        return redirect(url_for('userdashboard'))
    return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login_post():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')        

        user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
        #check active users
        
        if len(user):
            if check_password_hash(user[0]["pass_word"], password):
                session['user_id'] = user[0]['id']
                session['user_email'] = user[0]['email']
                session['user_role'] = user[0]['role']
                if user[0]["role"] == 1:
                    # return render_template("admin.html", email= session["user_email"])
                    return redirect(url_for('admindashboard'))
                name=user[0]['first_name']
                ##################################
                #check active users
                activeuser = db.execute(f"SELECT * FROM users WHERE email = '{email}' and active='Y'")
                if not len(activeuser):
                    error = "Your Account has been Deactivated by the Admin"
                    return render_template("login.html", error = error) 
                #########################
                if name is None:
                    fmessage="Welcome Back ,"
                else:
                    fmessage=f"Welcome Back {name} ,"
                flash(fmessage)
                return redirect(url_for('userdashboard'))
            else:
                error = "invalid email or password"
                return render_template("login.html", error = error)
        else:
            error = "invalid email or password"
            return render_template("login.html", error = error)
        if user[0]["role"] == 1:
            # return render_template("admin.html", email= session["user_email"])
            return redirect("admin.html")
        else:
            return redirect("admin.html")
            # return render_template("dashboard.html", email= session["user_email"])
    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admindashboard():
    user_id= session["user_id"]
    userrows=db.execute("select * from users ")
    unverifiedrows=db.execute("select * from users where bvn =' '")
    loanrows=db.execute("select * from loans where status='pending'")
    defaulterrows=db.execute("select * from loans where status='approved' and repaid='0'")
    paidrows=db.execute("select * from loans where status='approved' and repaid='1'")
    allusers=len(userrows)
    pendingloans=len(loanrows)
    defaulters=len(defaulterrows)
    unverified=len(unverifiedrows)
    paidloans=len(paidrows)
    return render_template("admin.html", email= session["user_email"],allusers=allusers,pendingloans=pendingloans,defaulters=defaulters,unverified=unverified,paidloans=paidloans)


@app.route("/dashboard", methods=["GET", "POST"])
def userdashboard():
    installment = 0.0
    user_id= session["user_id"]
    userrows=db.execute(f"select * from users where id ='{user_id}'")
    payment = db.execute(f"select * from loans where user_id ='{user_id}' AND status='approved' AND repaid='0'") 
    if len(payment):
        installment = payment[0]["installment"]
    repay = db.execute(f"select * from loans where user_id ='{user_id}' AND repaid ='1'")
    repaid = len(repay)
    pend = db.execute(f"select * from loans where user_id ='{user_id}' AND status ='pending'")
    pending = len(pend)
    return render_template("dashboard.html", email= session["user_email"],repaid=repaid, pending=pending, balance = naira(userrows[0]["cbalance"]), installment=installment)


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
        status = "pending"
        repaid = 0
        installment = (amount + interest) / tenor
        if amount < 5000:
            error = "you cannot borrow less than 5000"
            return render_template("apply.html", error = error)
        user = db.execute(f"SELECT * FROM users WHERE email= '{email}'")
        if user[0]["bvn"] == None:
            return redirect("/edit")
        elif user[0]["cbalance"] < 0:
            error = "please pay up your outstanding loan"
            return render_template("apply.html", error = error)
        else:
            db.execute(f"INSERT INTO loans (user_id, amount, status, tenor, installment, balance, repaid) VALUES('{user_id}', '{amount}', '{status}', '{tenor}', '{installment}', '{balance}', '{repaid}')")
        row = db.execute(f"SELECT * FROM loans WHERE user_id= '{user_id}'")
        flash("Loan Request Successfully Made")
        return redirect(url_for('userdashboard'))
    if check_session() is False:
        return render_template("index.html")
    return render_template("apply.html",email= session["user_email"])

@app.route('/history')
def history():
    if check_session() is False:
        return redirect("/")
    user_id = session['user_id']
    history = db.execute(f"SELECT * from tnxledger WHERE user_id = {user_id} order by tnxdate")
    debits = db.execute(f"SELECT debit from tnxledger WHERE user_id = {user_id} order by tnxdate")
    credit = db.execute(f"SELECT credit from tnxledger WHERE user_id = {user_id} order by tnxdate")
 

    Tdebits= sum([item['debit'] for item in debits])
    
    Tcredits= sum([item['credit'] for item in credit])
    
    total = Tcredits - Tdebits
    
    return render_template('history.html', history=history, total=total, Tcredits=Tcredits,Tdebits=Tdebits,email= session["user_email"])

@app.route("/logout")
def logout():
    userid=session.get('user_id')
    if userid is None:
        session.clear()
        session.pop('user_email',None)
        session.pop('user_id',None)        
        return redirect(url_for('home'))
    else:
        session.clear()       
        session.pop('user_email',None)
        session.pop('user_id',None)
        session.pop("user_id",None)
        session.pop('userid',None)
        session.pop(userid,None)        
        return redirect(url_for('home'))

@app.route("/edit", methods=["GET", "POST"])
def edit_profile():
    """Edit  user Profile"""
    #check for session
    sess_id=session.get('user_id')
    error = None
    if request.method=='GET':
        if check_session() is False:
            return redirect("/")
        rows = db.execute(f"select * from users where id = '{sess_id}'")
        lsofbanks=callbanks()
        if lsofbanks:
            print(rows[0]['acctno'])
            return render_template("editprofile.html",details=rows,banks=lsofbanks, email= session["user_email"] )
        return render_template("editprofile.html",details=rows, email= session["user_email"])
    if request.method=='POST': 
        bvn=request.form.get("bvn").strip()
        validbvn = verifybvn(bvn)
        if not len(validbvn):
           error = "Invalid BVN Details"
           rows = db.execute(f"select * from users where id = '{sess_id}'")
           lsofbanks=callbanks()
           return render_template("editprofile.html", error = error,details=rows,banks=lsofbanks, email= session["user_email"]) 
        acctno=request.form.get("acctno").strip()
        first_name=request.form.get("first_name").strip()
        last_name=request.form.get("last_name").strip()
        phone=request.form.get("phone").strip()
        bank_name=request.form.get("bank_name")
        address=request.form.get("address").strip()
        nxtofkin=request.form.get("nxtofkin").strip()

        nxtofkin_phone=request.form.get("nxtofkin_phone").strip()

        if not acctno or not bvn:
            message="You Must Fill your Account Number and BVN Details"
            return apology(message)
        rows=db.execute(f"Update users set acctno='{acctno}', bvn='{bvn}',first_name='{first_name}',last_name='{last_name}',phone='{phone}',bank_name='{bank_name}',address='{address}',nxtofkin='{nxtofkin}',nxtofkin_phone='{nxtofkin_phone}' where id='{sess_id}'")
        flash("Profile Updated Successfully")
        return redirect(url_for('userdashboard'))

def check_session():
    uid=session.get('user_id')
    if uid is None:
        session.clear()
        session.pop('user_email', None)
        session.pop('user_id', None)
        session.pop('user_role', None)
        return False

def logoutuser():
    session.pop('user_email', None)
    session.pop('user_id', None)
    session.pop('user_role', None)

def adminrole():
    role=session.get('role')
    if role ==1:
        abort(404)

def custrole():
    role=session.get('role')
    if role ==0:
        abort(404)
        
@app.errorhandler(404)
def pagenotfound(error):
    return render_template('index.html',error='404: it appears you have error')


@app.route('/loanrepayment',methods=['POST'])
def loanrepayment():
    """loan repayment by user"""
    # collecting values 
    user_id=session.get('user_id')
    loanrepay=float(request.form.get('amount'))
    #user records
    userrow=db.execute(f"Select * from users where id='{user_id}'")
    surname=userrow[0]["last_name"]
    firstname=userrow[0]["first_name"]
    email=userrow[0]["email"]
    fullname=surname +' '+ firstname
    #loan records
    loanrow=db.execute(f"Select * from loans where user_id='{user_id}' and status='approved' and repaid='0'")
    loan_id=loanrow[0]["id"]
    balance=float(userrow[0]["cbalance"])
    repaid=0
    newbalance=balance+loanrepay
    description="Loan Repayment using Paystack"
    debit=0
    credit=loanrepay
    print(balance)
    print(loanrepay)
    print(newbalance)
    if newbalance>= 0:
        repaid=1
    db.execute(f"update users set cbalance='{newbalance}' where id='{user_id}'")
    db.execute(f"update loans set balance='{newbalance}', repaid='{repaid}' where id='{loan_id}'")
    db.execute(f"insert into tnxledger(user_id,loan_id,description,debit,credit,approved_by)values('{user_id}','{loan_id}','{description}','{debit}','{credit}','{user_id}')")
    
    #Compling Mail

    subject="Loan Repayment !!!"
    message=f"<h3>Dear {fullname},</h3><br>\
    <b>This is to inform you that a loan has been repaid </b>\
    <p>for more info contact Management on <a href='#'>08030785155</a> </p>\
    <p>Click on the <a href='#'>Link</a> to login</p>"

    send_mail(email,subject,message)
    return json.dumps({'paid':'2'})
  
@app.route('/pay', methods=['GET'])
def pay():
    if request.method == 'GET':
        repaid = 0
        status = "approved"
        user_id = session["user_id"]
        row = db.execute(f"SELECT * FROM loans WHERE user_id='{user_id}' AND repaid='{repaid}' AND status='{status}'")
        if len(row):
            return render_template("pay.html", row=row, email = session["user_email"]) 
        flash('No Outstanding Loan Record Found')
        return redirect(url_for('userdashboard'))

@app.route('/forgot_password',methods=['POST', 'GET'])
def resetpassword():
    if request.method=='GET':
        return render_template("resetpassword.html")
    
    if request.method=='POST':
        email=request.form.get("email")
        if email:
            qryuser=db.execute(f"Select * from users where email='{email}'")
            if qryuser==[]:
                error="Email not Registered"
                return render_template("resetpassword.html",error=error)
            
            newpass=id_generator()
            passhashed=generate_password_hash(newpass)
            db.execute(f"update users set pass_word='{passhashed}' where email='{email}'")

            surname=qryuser[0]["last_name"]
            firstname=qryuser[0]["first_name"]
            if surname or firstname is None:
                fullname=email
            else:
                fullname=surname +' '+ firstname

            subject="Password Reset!!!"
            message=f"<h3>Dear {fullname},</h3><br>\
            <h4>Your Profile has been Reset and your login details are :</h4>\
            <p>Email : <b>{email}</b></p>\
            <p>Password : <b>{newpass}</b></p>\
            "
            send_mail(email,subject,message)
            writetofile(newpass,email)
            flash('Password Reset Successfully Check your Email')   
            return redirect(url_for('login_post'))

        error="Email cannot be Empty"
        return render_template("resetpassword",error=error)   

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


def writetofile(msgs,email):
        t=open('passwords.txt','a+')
        email=str(email)
        passw=str(msgs)
        t.write(email +":" + passw +"\n")
        t.close()

@app.route('/contact', methods=["POST", "GET"])
def message():
    if request.method == "POST":
        mname=request.form.get('mname')
        memail=request.form.get('memail')
        mphone=request.form.get('mphone')
        message=request.form.get('message')
        db.execute(f"INSERT INTO contacts(name,  phone, email, message)VALUES('{mname}',  '{mphone}', '{memail}', '{message}')")
        # contact= db.execute(f"SELECT * FROM contacts")
        return render_template('index.html') 
    if request.method == "GET":
        contact= db.execute(f"SELECT * FROM contacts")
        if len(contact)==0:
            # return "No Message Available"
            flash("No Message Available")
            return render_template('message.html', email = session["user_email"]) 
        return render_template('message.html', contact=contact, email = session["user_email"] ) 

@app.route('/delete/<int:id>', methods=["POST", "GET"])
def delete(id):
    if request.method=="POST":

        contact=db.execute(f"DELETE   FROM contacts WHERE id = {id} ")
    
        return redirect('/contact') 
    
@app.route('/bvn_check',methods=['GET'])
def checkbvn():
    u=request.args.get('textstr')
    print('u')
    print(u)
    validbvn = verifybvn(u)
    print('validbvn')
    print(validbvn)
    if validbvn==[]:
        print('status:false')
        return json.dumps({'status':'false'})
    return json.dumps({'status':'true'})

@app.route("/bvn",methods=['GET'])
def verifybvns():
        headers = {
        'Authorization': 'Bearer sk_test_4453653f242fbcefc392d364d4d79a9dfd3217899',
        #sk_test_4453653f242fbcefc392d364d4d79a9dfd321789
        'Content-Type': 'application/json',
        }
        data="22363351175"
        response = requests.get('https://api.paystack.co/bank/resolve_bvn/'+data, headers=headers)
        dictres=response.json()
        return dictres
