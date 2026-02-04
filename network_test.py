#!/usr/bin/env python3
"""Test network connectivity to PixelDrain from Render"""

import requests
import socket
import os

def test_pixeldrain_connectivity():
    """Test if we can reach PixelDrain from Render"""
    
    print("Testing PixelDrain connectivity...")
    
    # Test 1: DNS Resolution
    try:
        ip = socket.gethostbyname('pixeldrain.com')
        print(f"✅ DNS Resolution: pixeldrain.com -> {ip}")
    except Exception as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # Test 2: HTTPS Connection
    try:
        response = requests.get('https://pixeldrain.com', timeout=10)
        print(f"✅ HTTPS Connection: Status {response.status_code}")
    except Exception as e:
        print(f"❌ HTTPS Connection failed: {e}")
        return False
    
    # Test 3: API Endpoint
    try:
        api_key = os.getenv('PIXELDRAIN_API_KEY', '')
        if api_key:
            response = requests.get('https://pixeldrain.com/api/user/info', 
                                  auth=('', api_key), timeout=10)
            print(f"✅ API Test: Status {response.status_code}")
        else:
            print("⚠️  No API key, skipping API test")
    except Exception as e:
        print(f"❌ API Test failed: {e}")
    
    # Test 4: Alternative endpoints
    endpoints = [
        'https://pixeldrain.com',
        'https://www.pixeldrain.com',
        'https://api.pixeldrain.com'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return True

if __name__ == '__main__':
    test_pixeldrain_connectivity()