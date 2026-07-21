from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid


class User:
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        print(user)
        return jsonify(user), 200

    def signup(self):
        print(request.form)

        # creating user object
        kuralList = [[0]*10]*133
        adhigaramList = [0]*133
        
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "cpassword": request.form.get('cpassword'),
            "points":{
                "stars":{
                    "total" : 0,
                    "kurals_completed": list(kuralList)
                },
                "diamonds":{
                    "total" : 0,
                    "drag_drop":list(adhigaramList),
                    "fillups":list(adhigaramList)
                }
            }
        }

        # Password Encryption
        user['password'] = pbkdf2_sha256.encrypt(user['password'])
        # user['cpassword'] = user['password']

        # check for existing email id
        if db.user_details.find_one({"email": user['email']}):
            return jsonify({"error": "Email already exists"}), 400

        if db.user_details.insert_one(user):
            return self.start_session(user)

        return jsonify({"error": "Signup failed"}), 400

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        user = db.user_details.find_one({"email": request.form.get('email')})

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        return jsonify({"error": "மின்னஞ்சல் அல்லது கடவுச்சொல் தவறு"}), 401
