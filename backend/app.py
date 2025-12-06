from flask import Flask, jsonify , request
from flask_cors import CORS 
import mysql.connector

app = Flask(__name__)
CORS(app)   # allow frontend (React) to communicate

db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'inventory_db',
    port = 3307
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return "Backend is running successfully"

if __name__ == "__main__":
    app.run(debug=True)