from cs50 import SQL
from . import app,db,mail
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json,url_for
# from flask_session import Session
from .users import check_session
from flask_mail import Mail, Message
from .helpers import send_mail, naira
from .api import verifybvn

@app.route("/approval/<uid>", methods=["GET", "POST"])
def loan_approval(uid):
    """Approval for loan """
    sess_id=session.get('user_id')
    # sess_id=1
    if request.method=='GET':
        if  check_session() is False:
            return redirect("/")
        loanid = int(uid)
        loan = db.execute(f"SELECT * FROM loans WHERE id= '{loanid}' and status ='pending'")
        if loan == []:
            return redirect(url_for('admindashboard'))
        user_id = loan[0]["user_id"]
        userdetails = db.execute(f"SELECT * FROM users WHERE id= '{user_id}'")
        bvn=userdetails[0]["bvn"]
        bvndetails=verifybvn(bvn)
        return render_template("approval.html",userdetails=userdetails[0],bvndetails=bvndetails, loan=loan[0], uid=uid)
    if request.method=='POST':
        loansrec=db.execute(f"select * from loans where id='{uid}' and status= 'pending'")
        user_id=loansrec[0]["user_id"]
        loan_id=loansrec[0]["id"]
        description="Capital Loan Disbursement"
        credit=0
        debit=loansrec[0]["amount"]
        tenor=loansrec[0]["tenor"]
        rowuser=db.execute(f"select * from users where id='{user_id}'")
        db.execute(f"insert into tnxledger(user_id,loan_id,description,debit,credit,approved_by)values('{user_id}','{loan_id}','{description}','{debit}','{credit}','{sess_id}')")
        balance=rowuser[0]["cbalance"]
        email=rowuser[0]["email"]
        newbalance=balance-debit
        db.execute(f"update users set cbalance='{newbalance}' where id='{user_id}'")
        db.execute(f"update loans set status='approved' where id='{uid}'")
        ###############################################################
        surname=rowuser[0]["last_name"]
        firstname=rowuser[0]["first_name"]
        subject="Loan Approved !!!"
        fullname=surname +' '+ firstname
        # to="loanapproved@decacredit.com.ng"
        message=f"<h3>Dear {fullname},</h3><br>\
            <h4>Your Loan has been Approved and Disbursed details are :</h4>\
            <p>Loan ID : <b>{loan_id}</b></p>\
            <p>Amount : <b>{debit}</b></p>\
            <p>Tenor : <b>{tenor} Month(s)</b></p>\
            <p>Click on the <a href='https://abc.com/'>Link</a> to login</p>"  
        send_mail(email, subject, message)
        ############################################################################################
        flash("User Records Updated")
        return redirect(url_for('admindashboard'))
        
@app.route("/outstanding")
def outstanding():
    """admin view oustanding loan"""
    if  check_session() is False:
        return redirect("/")
    user_id=session.get('user_id')
    email=session.get('user_email')        
    status = "approved"
    repaid = 0
    outstanding = db.execute(f"SELECT * FROM loans WHERE status = '{status}' AND repaid = '{repaid}'")
    sumloan=db.execute(f"select sum(balance) as bal from loans where status = '{status}' AND repaid = '{repaid}'")
    T_sum=sumloan[0]["bal"]
    if T_sum is None:
        T_sum=0
    return render_template("outstanding.html", outstanding = outstanding,email=email,total=naira(T_sum))

@app.route('/request')
def pending():
    user_id=session.get('user_id')
    email=session.get('user_email')
    if  check_session() is False:
        return redirect("/")    
    status = "pending"
    repaid = 0
    pending = db.execute(f"SELECT * FROM loans WHERE status = '{status}'")
    sumloanpend=db.execute(f"select sum(amount) as bal from loans where status = '{status}' AND repaid = '{repaid}'")
    T_sum=sumloanpend[0]["bal"]
    if T_sum is None:
        T_sum=0
    return render_template("request.html", pending=pending,email=email,total=naira(T_sum))

@app.route('/loans')
def loan():
    if  check_session() is False:
        return redirect("/")
    user_id=session.get('user_id')
    email=session.get('user_email')   
    amt = 1
    loans = db.execute(f"SELECT * FROM loans WHERE repaid = '{amt}'")
    return render_template("loan.html", loans = loans,email=email)

@app.route('/loan_reject',methods=['GET'])
def rejectloan():
    u=request.args.get('textstr')
    db.execute(f"update loans set status= 2 where id='{u}'")
    return json.dumps({'rejected':'1'})
    user_id=session.get('user_id')
    userrow=db.execute(f"Select * from users where id='{user_id}'")
    surname=userrow[0]["last_name"]
    firstname=userrow[0]["first_name"]
    email=userrow[0]["email"]
    fullname=surname +' '+ firstname
    subject="Loan Rejected !!!"
    message=f"<h3>Dear {fullname},</h3><br>\
    <b>This is to inform you that your Loan has been Rejected by the Admin </b>\
    <p>for more info contact Management on <a href='#'>08030785155</a> </p>\
    <p>Click on the <a href='#'>Link</a> to login</p>"  
    loanid=request.args.get('textstr')
    db.execute(f"update loans set status= 2 where id='{loanid}'")
    send_mail(email,subject,message)
    return json.dumps({'rejected':'2'})
