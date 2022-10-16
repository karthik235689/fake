from flask import Flask, render_template, request, url_for
import pandas as pd
import numpy as np
import joblib,os
import pickle
from contextlib import redirect_stderr
import email
from flask import Blueprint , render_template , url_for , redirect , request , session
import bcrypt
from twilio.rest import Client
import random
import smtplib
import math
from pymongo import MongoClient
import os 

connection_string="mongodb+srv://karthik:karthik@cluster0.rctxccl.mongodb.net/?retryWrites=true&w=majority"
client=MongoClient(connection_string)
dataSeesaws=client.Seesaws
collection=dataSeesaws.Users


app = Flask(__name__)
app.config['SECRET_KEY']="8aEaAjuuAXM8aC4"


@app.route("/login" , methods=['GET','POST'])
def login():
    emailid=request.form.get("email")
    password1=request.form.get("password")
    return render_template("Login.html")


@app.route("/register" , methods=['GET','POST'])
def register():
    if request.method == "POST":
        firstname=request.form.get("fname")
        lastname=request.form.get("lname")
        emailid=request.form.get("email")
        mobilenumber=request.form.get("phonenumber")
        password1=request.form.get("password")
        password2=request.form.get("confirmpassword")
        if password1 != password2:
                message = 'Passwords should match!'
                return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
            user_input = {'firstName': firstname, 'lastName': lastname, 'email': emailid , 'Mobile': mobilenumber , 'Password': hashed}
            collection.insert_one(user_input)
            return render_template('VerifyMobile.html')
    return render_template("Register.html")

def generateotp():
    return random.randrange(100000,999999)

def getotpapi(number):
    account_sid="AC716e7536612de6dbc5a9f4105a82639d"
    app_token="e87735f2f7a3f07bbfded4f1122102cf"
    client=Client(account_sid,app_token)
    otp=generateotp()
    session['response']=str(otp)
    body='Your OTP is ' + str(otp)
    message=client.messages.create(
                            from_='+15736724358',
                            body=body,
                            to=number
    )
    if message.sid:
        return True 
    else:
        return False
    
@app.route("/verify/mobile",methods=["POST"])
def verify_mobile():
    if request.method == "POST":
        number=request.form.get("mnumber")
        print("number",number)
        number="+91"+str(number)
        val=getotpapi(number)
        if val:
            return render_template('Enterotp_number.html')
    return render_template("VerifyMobile.html")

@app.route('/verify/mobile/otp',methods=['POST'])
def validate():
    otp=request.form.get('otp')
    if 'response' in session:
        s=session['response']
        print(otp)
        print(session)
        session.pop('response',None)
        if s==otp:
            return render_template('VerifyEmail.html')
        else:
            return 'You are not apporized, Sorry!!'
    return render_template('Enterotp_number.html')

def generateotp_email():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    otp = OTP #+ " is your OTP"
    return otp

def getotpapi_email(emailid):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("seesawsofficial@gmail.com", "pinpekzdqvrcscqq")
    otp=generateotp_email()
    msg=otp + " is your OTP"
    s.sendmail('&&&&&&&&&&&&&&&&', emailid, msg)
    session['response']=str(otp)
    return True

@app.route("/verify/email",methods=['POST','GET'])
def verify_email():
    emailid = request.form.get('emailid')
    print(emailid)
    val=getotpapi_email(emailid)
    if val:
        return render_template('Enterotp_email.html')

@app.route('/verify/email/otp',methods=['POST'])
def validate_email():
    otp=request.form.get('otp')
    if 'response' in session:
        s=session['response']
        session.pop('response',None)
        if s==otp:
            return redirect("/login")
        else:
            return 'You are not apporized, Sorry!!'
    return render_template('Enterotp_email.html')


@app.route('/verifylogin',methods=['POST'])
def logged_in():
    if request.method == "POST":
        EmailId = request.form.get("email_address")
        Password = request.form.get("password")
        p1 = collection.find_one({"email": EmailId})
        if Password==p1["Password"]:
            return render_template('Home.html')
        else:
            return redirect(url_for("login"))





if __name__ == "__main__":
    app.run(debug=True)