from cs50 import SQL
from . import app,db,mail
from flask import Flask, flash, jsonify, redirect, render_template, request, session,json
from flask_session import Session
from .users import check_session
from flask_mail import Mail, Message
from .helpers import send_mail
from .api import verifybvn

@app.route("/approval/<uid>", methods=["GET", "POST"])
def loan_approval(uid):
    """Approval for loan """
    #check for session
    # sess_id=session["user_id"]
    sess_id=1
    if not check_session(sess_id):
        return redirect("/")
    if request.method=='GET':
        userrow=db.execute(f"select * from users where id={sess_id}")
        userdetails=userrow[0]
        bvn=userrow[0]["bvn"]
        bvndetails=verifybvn(bvn)
        print(bvndetails)
        return render_template("approval.html",userdetails=userdetails,bvndetails=bvndetails)
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
def apply():
    """admin view oustanding loan"""
    status = "active"
    repaid = 0
    outstanding = db.execute(f"SELECT * FROM loans WHERE status = '{status}' AND repaid = '{repaid}'")
    return render_template("outstanding.html", oustanding = outstanding)

@app.route('/request')
def pending():
    status = "pending"
    pending = db.execute(f"SELECT * FROM loan WHERE status = '{status}'")
    return render_template("request.html", pending=pending)
