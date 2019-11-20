from cs50 import SQL
from . import app,db,mail
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
# from flask_session import Session
from .users import check_session
from flask_mail import Mail, Message
from .helpers import send_mail
from .api import verifybvn

@app.route("/approval/<uid>", methods=["GET", "POST"])
def loan_approval(uid):
    """Approval for loan """
    sess_id=session.get('user_id')
    # sess_id=1
    if request.method=='GET':
        if  check_session() is False:
            return redirect("/")
        userrow=db.execute(f"select * from users where id={sess_id}")
        userdetails=userrow[0]
        bvn=userrow[0]["bvn"]
        bvndetails=verifybvn(bvn)
        print(bvndetails)
        return render_template("approval.html",userdetails=userdetails,bvndetails=bvndetails,uid=uid)
    if request.method=='POST':
        loansrec=db.execute(f"select * from loans where id='{uid}' and status= 0")
        print(loansrec)
        user_id=loansrec[0]["user_id"]
        loan_id=loansrec[0]["id"]
        description="Capital Loan Disbursement"
        credit=0
        debit=loansrec[0]["amount"]
        tenor=loansrec[0]["tenor"]
        rowuser=db.execute(f"select * from users where id='{user_id}'")
        db.execute(f"insert into tnxledger(user_id,loan_id,description,debit,credit,approved_by)values('{user_id}','{loan_id}','{description}','{debit}','{credit}','{sess_id}')")
        print(rowuser)
        balance=rowuser[0]["cbalance"]
        email=rowuser[0]["email"]
        newbalance=balance-debit
        db.execute(f"update users set cbalance='{newbalance}' where id='{user_id}'")
        db.execute(f"update loans set status='1' where id='{uid}'")
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
        return redirect("/userdashboard")
        
@app.route("/outstanding")
def outstanding():
    """admin view oustanding loan"""
    if  check_session() is False:
        return redirect("/")
    status = "active"
    repaid = 0
    outstanding = db.execute(f"SELECT * FROM loans WHERE status = '{status}' AND repaid = '{repaid}'")
    return render_template("outstanding.html", oustanding = outstanding)

@app.route('/request')
def pending():
    if  check_session() is False:
        return redirect("/")    
    status = "pending"
    pending = db.execute(f"SELECT * FROM loan WHERE status = '{status}'")
    return render_template("request.html", pending=pending)

@app.route('/loans')
def loan():
    if  check_session() is False:
        return redirect("/")    
    amt = 1
    loans = db.execute(f"SELECT * FROM loan WHERE repaid = '{amt}'")
    return render_template("loan.html", loans = loans)

@app.route('/loan_reject',methods=['GET'])
def rejectloan():
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
