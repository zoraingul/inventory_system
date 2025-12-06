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
        

@app.route('/categories' , methods = ['POST'])
def create_category():
    data = request.get_json()
    category_name = data.get('category_name')
    description = data.get('description')
    created_by = data.get('created_by')
    
    #validation
    if not category_name or not created_by:
        return jsonify({'error' : 'Category name and creator are required'}) , 400
    
    try:
        cursor.execute(
            "insert into categories (category_name , description , created_by) VALUES (%s , %s , %s)" , (category_name , description , created_by)
    )
        db.commit()
        return jsonify({'message': 'Category created successfully'})
    
    except mysql.connector.Error as e:
        return jsonify({'error' , str(e)}) , 500
    
@app.route('/catetgories' , methods = ["GET"])
def get_categories():
    cursor.execute("Select * from categories")
    categories = cursor.fetchall()
    return jsonify(categories)
    
    
@app.route('/categories/<int:category_id>' , methods = ["PUT"])
def update_category(category_id):
    
    data = request.get_json()
    category_name = data.get('category_name')
    description = data.get('description')
    
    if not category_name or not description: #created by confusion
        return jsonify({'error' : 'Nothing to update'})

    try:
        cursor.execute(
            "Update categories SET category_name= %s , description=%s where category_id=%s" , (category_name ,description , category_id)
        )
        db.commit()
        return jsonify({'message' : "Categry updated successfully"})
    except mysql.connector.Error as e:
        return jsonify({'error' : str(e)}) , 500

@app.route('/categories/<int:category_id>' , methods = ['DELETE'])
def delete_category(category_id):
    try:
        cursor.execute("DELETE from category where category_id=%s" , (category_id))
        db.commit()
        return jsonify({'message' : 'Category Deleted Successfully'})
    except mysql.connector.Error as e:
        return jsonify ({'error' : str(e)}) , 500



@app.route('/')
def home():
    return "Backend is running successfully"

if __name__ == "__main__":
    app.run(debug=True)