import pyrebase
import firebase_admin
from firebase_admin import credentials, db

def firebaseConfig():
    return {
        "apiKey": "AIzaSyD0Mz01-HXTP1TyC_17XD5BMNEABBucino",
        "authDomain": "employer-management-syst-15264.firebaseapp.com",
        "databaseURL": "https://employer-management-syst-15264-default-rtdb.firebaseio.com/",
        "projectId": "employer-management-syst-15264",
        "storageBucket": "employer-management-syst-15264.appspot.com",
        "messagingSenderId": "188357042151",
        "appId": "1:188357042151:web:0ff9f1ee9097f21f7d2742",
        "measurementId": "G-C61B3H8BRL"
    }

cred = credentials.Certificate("employer-management-syst-15264-firebase-adminsdk-6elp0-6be6754ffa.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://employer-management-syst-15264-default-rtdb.firebaseio.com/'
})

firebase = pyrebase.initialize_app(firebaseConfig())  # Notice the parentheses after firebaseConfig
auth = firebase.auth()
