from flask import Flask, jsonify , request
from flask_cors import CORS 
import mysql.connector
from werkzeug.security import generate_password_hash , check_password_hash

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

@app.route('/register' , methods= ["POST"])
def register():
    data = request.get_json() # get data from frontend 
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role' , 'student')
    
    #validation 
    if not username or not email or not password:
        return jsonify({'error': 'Please provide all fields'})

    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            "insert into users (username , email , password_hash , role) VALUES (%s , %s , %s , %s)" , (username , email , password_hash , role) #sql insert
        )
        db.commit() #save changes to the database
        return jsonify({'message': 'User registered successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'error' : 'username or email already exists'}) , 400


#login route
@app.route('/login' , methods = ["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    #input validation
    if not username or not password:
        return jsonify({'error': 'Please provide username and password'}) , 400
    
    #fetch user from db
    cursor.execute(
        "select * from user where username = %s" , (username,)
    )    
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'error': 'Invalid username or password'}) , 401
    
    #check password
    
    if check_password_hash(user['password_hash'], password):
        #successful login
        return jsonify ({
            'message' : 'Login Successful',
            'user' : {
                'id' : user['user_id'],
                'username' : user['username'],
                'role' : user['role']
            }
        })
    else:
        return jsonify({'error': 'Inalid username or password'}) , 401
        

@app.route('/')
def home():
    return "Backend is running successfully"

if __name__ == "__main__":
    app.run(debug=True)