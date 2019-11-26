from flask import Flask, request,abort,redirect,url_for,make_response,render_template
import json
from flask import jsonify
import requests,datetime
from werkzeug.security import generate_password_hash,check_password_hash

def verifybvn(data):
        headers = {
        'Authorization': 'Bearer sk_test_4453653f242fbcefc392d364d4d79a9dfd3217899',
        'Content-Type': 'application/json',
        }
        # data=""
        response = requests.get('https://api.paystack.co/bank/resolve_bvn/'+data, headers=headers)
        # response = {
        #     "status": True,
        #     "message": "BVN resolved",
        #     "data": {
        #         "first_name": "WES",
        #         "last_name": "GIBSONS",
        #         "dob": "14-OCT-96",
        #         "mobile": "09022092102",
        #         "bvn": "21212917741"
        #     },
        #     "meta": {
        #         "calls_this_month": 1,
        #         "free_calls_left": 9
        #     }
        #     }
        array = []
        if response:
            response=response.json()
            print('bvn details')
            print(response)
            for items in response["data"].values():
                array.append(items)
            # dictresponse=response.json()
            return(array)
        else:
            return(array)
            
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
         
