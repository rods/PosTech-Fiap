"""
Simple test to verify JWT functionality works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.auth import create_access_token, SECRET_KEY, ALGORITHM
    import jwt
    
    print("✅ JWT imports working correctly")
    
    # Test token creation
    test_data = {"sub": "admin"}
    token = create_access_token(test_data)
    print(f"✅ Token created: {token[:50]}...")
    
    # Test token decoding
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"✅ Token decoded: {payload}")
    
    print("\n🎉 JWT functionality is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()