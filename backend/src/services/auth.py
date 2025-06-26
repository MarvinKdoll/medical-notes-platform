import os
import boto3
import hashlib
import jwt
import uuid
import json
from datetime import datetime, timedelta
print("auth.py file is being executed..")

#DB connection
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('medical-users')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, full_name):
    user_id = str(uuid.uuid4())
    try:
        existing = users_table.get_item(Key={'email': email})
        if 'Item' in existing: 
            return None, "Email already registered"
    except Exception:
        pass

    try:
        users_table.put_item(Item={
            'email': email, 
            'user_id': user_id, 
            'password_hash': hash_password(password),
            'full_name': full_name, 
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        })
        return user_id, "Success"
    except Exception as e:
        return None, f"Database error: {str(e)}"
    
def verify_login(email, password):
    try:
        response = users_table.get_item(Key={'email': email})
        if 'Item' not in response: 
            return None, "Invalid email or password"
        
        user = response['Item']
        if user['password_hash'] != hash_password(password):
            return None, "Invalid email or password"
        
        #create token with enviroment variable
        token_data = {
            'user_id': user['user_id'], 
            'email': user['email'], 
            'exp': datetime.utcnow() + timedelta(days=7)
        }

        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-replace-in-production')
        token = jwt.encode(token_data, secret_key, algorithm='HS256')

        return token, user 
    except Exception as e:
        return None, f"Login error: {str(e)}"
    
def verify_token(token):
    try:
        #same pattern - use enviroment variable 
        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-replace-in-production') 
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id'], payload['email']
    except jwt.ExpiredSignatureError:
        return None, "Token expired - please login again" 
    except jwt.InvalidTokenError:
        return None , "Invalid token"   
      
      #lambda function for handling auth endpoints
def auth_lambda_handler(event, context):
    try:
        #parse incoming request 
        body = json.loads(event['body'])
        path = event.get('path', '')

        #route to appropiate function based on url
        if '/signup' in path:
            user_id, message = create_user(
                email=body['email'],
                password=body['password'],
                full_name=body['full_name']
            )
            if user_id:
                return {
                    'statusCode': 201, 
                    'headers': {'Access-Control-Allow-Origin': '*'}, 
                    'body': json.dumps({'message': 'Account create succesfully'})
                }
            else:
                return {
                    'statusCode': 400, 
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': message})
                }
        elif '/login' in path:
            token, user_info = verify_login(body['email'], body['passsword'])

            if token:
                return {
                    'statusCode': 200, 
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'token': token, 
                        'user': {
                            'email': user_info['email'],
                            'full_name': user_info['full_name']
                        }
                    })
                }
            else:
                return {
                    'statusCode': 401, 
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': user_info})
                }
        else: 
            return {
                'statusCode': 404, 
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500, 
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }
def test_jwt_implementation():
    #test jwt generation and verification process
    print("Testing JWT Implementation")
    print('=' * 40)

    #check enviroment variable
    secret_key = os.environ.get('JWT_SECRET_KEY')
    if secret_key:
        print(f"JWT_SECRET_KEY found: {secret_key[:10]}...")
    else:
        print("JWT_SECRET_KEY not set, using fallback")

        #Test JWT creation and verifivxation without DB
        print("\n Testing JWT creation...")

        #create test token data
        test_token_data = {
            'user_id': 'test-user-123',
            'email': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(days=7)
        } 
        #generate token 
        secret = secret_key or 'dev-fallback-key-CHANGE-IN-PRODUCTION'
        test_token = jwt.encode(test_token_data, secret, algorithm='HS256')
        print("\nTesting JWT verification...")

        try: 
            decoded = jwt.decode(test_token, secret, algorithm=['HS256'])
            print(f"Token verified successfully")
            print(f" User ID: {decoded['user_id']}")
            print(f" Email {decoded['email']}")
            print(f" Expires: {datetime.fromtimestamp(decoded['exp'])}")

            return True
        except Exception as e:
            print(f" Token verification failed: {str(e)}")
            return False

    
    
if __name__ == "__main__":
    print(" Testing JWT implementation..")
    test_jwt_implementation()
   