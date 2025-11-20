import requests
import time
import sys

BASE_URL = "http://localhost:5001"

def test_styles():
    print("Testing /api/styles...")
    try:
        response = requests.get(f"{BASE_URL}/api/styles")
        if response.status_code == 200:
            print("✅ Styles endpoint working")
            print(f"Styles: {response.json()}")
        else:
            print(f"❌ Styles endpoint failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def test_platforms():
    print("\nTesting /api/platforms...")
    try:
        response = requests.get(f"{BASE_URL}/api/platforms")
        if response.status_code == 200:
            print("✅ Platforms endpoint working")
            print(f"Platforms: {response.json()}")
        else:
            print(f"❌ Platforms endpoint failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def test_generation():
    print("\nTesting /api/generate (Mock Mode)...")
    payload = {
        "title": "Test Article",
        "style": "Creative"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        if response.status_code == 200:
            data = response.json()
            if "images" in data and "generation_id" in data:
                print("✅ Generation endpoint working")
                return data["generation_id"]
            else:
                print("❌ Invalid response format")
                sys.exit(1)
        else:
            print(f"❌ Generation endpoint failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def test_download(generation_id):
    print("\nTesting /api/download...")
    payload = {
        "generation_id": generation_id,
        "selected_image_index": 0,
        "platform": "Hashnode"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/download", json=payload)
        if response.status_code == 200:
            print("✅ Download endpoint working")
            # Verify it's an image
            if response.headers['Content-Type'] == 'image/png':
                print("✅ Content-Type is image/png")
            else:
                print(f"❌ Unexpected Content-Type: {response.headers['Content-Type']}")
        else:
            print(f"❌ Download endpoint failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    test_styles()
    test_platforms()
    gen_id = test_generation()
    if gen_id:
        test_download(gen_id)
    
    print("\n🎉 All backend tests passed!")
