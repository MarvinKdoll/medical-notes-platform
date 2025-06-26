import json
import logging
from datetime import datetime, timedelta
from auth import create_user, verify_login, verify_token
import jwt
import os

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_jwt_process():
    """Debug the JWT generation and verification process step by step"""
    print("\n=== DEBUGGING JWT PROCESS ===")
    
    # Test user data
    test_email = "debug@test.com"
    test_password = "debugPassword123!"
    test_name = "Debug User"
    
    print("\n1. CHECKING JWT SECRET KEY...")
    secret_key = os.environ.get('JWT_SECRET_KEY')
    if secret_key:
        print(f"PASS JWT_SECRET_KEY found: {secret_key[:10]}...")
    else:
        print("FAIL JWT_SECRET_KEY not set!")
        print("Using fallback key for debugging...")
        secret_key = 'dev-secret-key-replace-in-production'
    
    print(f"\n2. CREATING TEST USER...")
    user_id, message = create_user(test_email, test_password, test_name)
    if user_id:
        print(f"PASS User created: {user_id}")
    else:
        print(f"FAIL User creation failed: {message}")
        return
    
    print(f"\n3. TESTING LOGIN AND TOKEN GENERATION...")
    token, user_info = verify_login(test_email, test_password)
    
    if token:
        print(f"PASS Token generated: {token[:50]}...")
        print(f"PASS User info: {user_info}")
    else:
        print("FAIL Login failed")
        return
    
    print(f"\n4. MANUALLY DECODING TOKEN (without verification)...")
    try:
        # Decode without verification to see what's inside
        decoded_unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"PASS Token payload: {json.dumps(decoded_unverified, indent=2, default=str)}")
        
        # Check expiration
        if 'exp' in decoded_unverified:
            exp_time = datetime.fromtimestamp(decoded_unverified['exp'])
            current_time = datetime.utcnow()
            print(f"PASS Token expires at: {exp_time}")
            print(f"PASS Current time: {current_time}")
            print(f"PASS Time until expiration: {exp_time - current_time}")
            
            if exp_time < current_time:
                print("FAIL TOKEN IS EXPIRED!")
            else:
                print("PASS Token is not expired")
    except Exception as e:
        print(f"FAIL Error decoding token: {e}")
    
    print(f"\n5. TESTING TOKEN VERIFICATION...")
    verified_user_id, verified_email = verify_token(token)
    
    if verified_user_id:
        print(f"PASS Token verified successfully")
        print(f"PASS Verified user ID: {verified_user_id}")
        print(f"PASS Verified email: {verified_email}")
    else:
        print("FAIL Token verification failed")
        
        # Let's debug why verification failed
        print("\n6. DEBUGGING VERIFICATION FAILURE...")
        
        # Try manual verification with the same secret
        try:
            decoded_verified = jwt.decode(token, secret_key, algorithms=['HS256'])
            print(f"PASS Manual verification successful: {decoded_verified}")
        except jwt.ExpiredSignatureError:
            print("FAIL Token is expired")
        except jwt.InvalidTokenError as e:
            print(f"FAIL Invalid token: {e}")
        except Exception as e:
            print(f"FAIL Verification error: {e}")
    
    return token, user_id

def test_api_simulation_with_debug(token):
    """Test API simulation with detailed debugging"""
    print("\n=== DEBUGGING API SIMULATION ===")
    
    # Simulate the exact same API request as in your test
    fake_event = {
        'headers': {
            'Authorization': f'Bearer {token}',
        },
        'body': json.dumps({
            'note': 'pt w/ cp x2d, plan: lab'
        })
    }
    
    print(f"\n1. EXTRACTING TOKEN FROM HEADERS...")
    auth_header = fake_event['headers'].get('Authorization', '')
    print(f"Authorization header: {auth_header}")
    
    if not auth_header.startswith('Bearer '):
        print(f"FAIL Missing auth header - Request rejected")
        return
    
    token_from_header = auth_header.replace('Bearer ', '')
    print(f"PASS Extracted token: {token_from_header[:50]}...")
    
    print(f"\n2. VERIFYING EXTRACTED TOKEN...")
    user_id, email = verify_token(token_from_header)
    
    if user_id:
        print(f"PASS Request authorized user: {email}")
        print(f"PASS Processing medical note...")
    else:
        print(f"FAIL Request rejected: invalid token")
        
        # Additional debugging
        print("\n3. ADDITIONAL TOKEN DEBUG...")
        if token != token_from_header:
            print("FAIL Token mismatch between original and extracted!")
            print(f"Original: {token[:50]}...")
            print(f"Extracted: {token_from_header[:50]}...")
        else:
            print("PASS Token matches original")

def run_enhanced_debug():
    """Run the complete debug sequence"""
    print("ENHANCED JWT DEBUG INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Debug the JWT process
        token, user_id = debug_jwt_process()
        
        if token and user_id:
            # Test API simulation
            test_api_simulation_with_debug(token)
        
        print("\n" + "=" * 60)
        print("DEBUG COMPLETE")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_enhanced_debug()