import json
from auth import create_user, verify_login, verify_token
import os

if not os.environ.get('JWT_SECRET_KEY'):
    os.environ["JWT_SECRET_KEY"] = 'test-secret-key-for-integration-testing'

def test_complete_auth_flow():
    print("Testing complete authentication flow")
    print("=" * 50)

    #test user update
    test_email = "doctor.test@hospital.com"
    test_password = "securePassword123"
    test_name = "Dr. Test User"

    #Step 1: Create user account
    print(" Creating user account...")
    user_id, message = create_user(test_email, test_password, test_name)

    if user_id:
        print(f" User creared: {user_id}")
    else:
        print(f" User creation failed: {message}")
        return False
    
    #Step 2: login(generate JWT)
    print("Logging in (generating JWT token)..")
    token, user_info = verify_login(test_email, test_password)

    if token: 
        print(f" Login successful")
        print(f" JWT Token: {token[:30]}...")
        print(f" USer: {user_info['full_name']}")
    else: 
        print(f" Login failed: {user_info}")
        return False
    
    #Step 3: Verify token (what happens on API request)
    print("Verifying JWT token...")
    verified_user_id, verified_email = verify_token(token)

    if verified_user_id:
        print(f"Token verification successful")
        print(f"User ID: {verified_user_id}")
        print(f" Email: {verified_email}")
    else: 
        print(f"Token verification failed {verified_email}")
        return False
    
    #Step 4: Test invalid token
    print("Testing invalid token...")
    fake_token = "fake.token.here"
    bad_user_id, error_msg = verify_token(fake_token)

    if not bad_user_id:
        print(f" Invalid token correctly rejected: {error_msg}")
    else:
        print(f" Security issues: fake token accepted")
        return False
    
    #Step 5: test wrong password
    print("Testing wrong password")
    bad_token, bad_message = verify_login(test_email, "wrongpassword")

    if not bad_token:
        print(f" Wrong password correctly rejected: {bad_message}")
    else: 
        print(f" Security issue: wrong password was accepted")
        return False
    
    print("n\ ALL TEST PASSED")
    print("Your JWT authentication system is working correctly")
    return True

def simulate_api_request():
    #simulate what happens when frontend makes api request
    print("n\ simulating api request")
    print("=" * 30)

    #generate a real token for testing 
    from auth import verify_login
    token, user_info = verify_login("doctor.test@hospital.com", "securePassword123")

    if not token:
        print("Failed to get valid token for simulation")
        return 

    #simulates what lamdba_function will do 
    fake_event = {
        'headers': {
            'Authorization': 'Bearer {token}'
        },
        'body': '{"note": "pt w/ cp x2d, plan: lab"}'
    }
     
    #extract token from Authorization header
    auth_header = fake_event.get('headers', {}).get('Authorization', '')
    if auth_header and auth_header.startswith('Bearer '):
        extracted_token = auth_header.replace('Bearer ', '')
       
        print(f" Received token: {token[:30]}...")

        #verify token 
        user_id, email = verify_token(token)
        if user_id:
            print(f" Request authorized user: {email}")
            print(f" Processing medical note...")
        else:
            print(f" Request rejected: {email}")
    else:
        print("No valid Authorization header")

def debug_token_verification(token):
    #debug helper
    
    print(f"Debug: Verifying token: {token[:30]}...")
    user_id, email = verify_token(token)

    if user_id:
        print(f"Debug: Token valid for user {email}")
        return True
    else:
        print(f"Debug: Token verification failed")
        return False
    
if __name__== "__main__":
    success = test_complete_auth_flow()
    simulate_api_request()




