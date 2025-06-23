#!/usr/bin/env python3
"""
Quick test to debug the web compilation issue
"""

import requests
import json

def test_web_compilation():
    """Test the web compilation endpoint with debugging"""
    
    # Simple test code
    test_code = '''
struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    p.x = 10;
    p.y = 20;
    return 0;
}
'''
    
    # Test data
    test_data = {
        'code': test_code,
        'optimization_level': 0,
        'ai_enhanced': False
    }
    
    print("🧪 Testing web compilation endpoint...")
    print(f"📝 Code length: {len(test_code)} characters")
    print(f"⚙️  Settings: optimization_level={test_data['optimization_level']}, ai_enhanced={test_data['ai_enhanced']}")
    
    try:
        # Make request to local web server
        response = requests.post(
            'http://localhost:5000/api/compile',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data),
            timeout=30
        )
        
        print(f"\n📡 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"\n✅ JSON Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print(f"\n🎉 SUCCESS!")
                print(f"Output: {result.get('result', 'No output')}")
                print(f"Compile time: {result.get('compile_time', 'Unknown')}ms")
            else:
                print(f"\n❌ COMPILATION FAILED!")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Message: {result.get('message', 'No message')}")
        else:
            print(f"\n📄 Raw response text:")
            print(response.text[:500])
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web server at http://localhost:5000")
        print("💡 Please start the web server first with: python web_app.py")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    test_web_compilation()
