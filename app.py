from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import JWTManager
import os
# Init app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# User Class/Model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100),  nullable=False)
  email = db.Column(db.String(144), unique=True, nullable=False)
  company = db.Column(db.String(100), nullable=False)
  phone = db.Column(db.String(144), nullable=False)
  password1 = db.Column(db.String(100), nullable=False)
  password2 = db.Column(db.String(144), nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

  def __init__(self, name, email, company, phone, password1, password2,image_file):
    self.name = name
    self.email = email
    self.company = company
    self.phone = phone
    self.password1 = password1
    self.password2 = password2
    self.image_file = image_file

# User Schema
class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'email','company','phone','password1','password2','image_file')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)



@app.route('/register', methods=['POST'])
def register():
    # Get the request parameters
    name = request.form.get('name', None)
    email = request.form.get('email', None)
    company = request.form.get('company', None)
    phone = request.form.get('phone', None)
    password1 = request.form.get('password1', None)
    password2 = request.form.get('password2', None)
    image_file = request.files.get('image_file', None)

    # Validate the request parameters
    if not name:
        return jsonify({"msg": "Missing name parameter"}), 400
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not company:
        return jsonify({"msg": "Missing company parameter"}), 400
    if not phone:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password1:
        return jsonify({"msg": "Missing create password parameter"}), 400
    if not password2:
        return jsonify({"msg": "Missing conform password parameter"}), 400

    # Save the user to the database
    user = User(name=name, email=email, company=company, phone=phone, password1=password1, password2=password2, image_file=image_file)
    db.session.add(user)
    db.session.commit()

    
    resp = jsonify({'Calculator': {
        'Name': user.name,
        'Email': user.email,
        'Company': user.company,
        'PhoneNumber':user.phone,
    }})
    return resp, 201


@app.route('/login', methods=['POST'])
def login():
    # Get the request parameters
    email = request.form.get('email', None)
    password1 = request.form.get('password1', None)

    # Validate the request parameters
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password1:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Check the user's credentials
    user = User.query.filter_by(email=email, password1=password1).first()
    if not user:
        return jsonify({"msg": "Invalid email or password"}), 401

    # Create and return a JWT access token and refresh token for the user
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    resp = jsonify({'name': user.name,'Access Token': access_token,'Refresh Token': refresh_token})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200



# Run Server
if __name__ == '__main__':
  app.run(debug=True)

