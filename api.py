from flask import Flask, request,abort,redirect,url_for,make_response,render_template
import json
from flask import jsonify
import requests,datetime
from werkzeug.security import generate_password_hash,check_password_hash

def verifybvn():
        headers = {
        'Authorization': 'Bearer sk_test_b7271cf4f04f90659c4d191481cecdeb1a1542988',
        'Content-Type': 'application/json',
        }
        data=""
        response = requests.get('https://api.paystack.co/bank/resolve_bvn/'+data, headers=headers)
        if response:
            dictresponse=response.json()
            return json.dumps(dictresponse)
            
def callbanks():
        headers = {
        'Authorization': 'Bearer sk_test_b7271cf4f04f90659c4d191481cecdeb1a154298',
        'Content-Type': 'application/json',
        }
        response = requests.get('https://api.paystack.co/bank', headers=headers)
        if response:
            dictresponse=response.json()
            array = []
            for i in range(len(dictresponse["data"])):
                array.append(dictresponse["data"][i]["name"])
            return array          