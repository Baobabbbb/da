#!/usr/bin/env python3
"""
Test des différents endpoints Wavespeed
"""

import requests
import time
import os
from dotenv import load_dotenv

def test_wavespeed_endpoints():
    """Tester différents endpoints Wavespeed"""
    
    load_dotenv()
    WAVESPEED_API_KEY = os.getenv('WAVESPEED_API_KEY')
    
    if not WAVESPEED_API_KEY:
        print("❌ Clé API Wavespeed manquante")
        return
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "aspect_ratio": "9:16",
        "duration": 10,
        "prompt": "test simple animation"
    }
    
    print("🧪 Test 1: Appel initial...")
    
    try:
        # Test 1: Appel initial
        response = requests.post(
            "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            prediction_id = result.get("data", {}).get("id") or result.get("id")
            
            if prediction_id:
                print(f"✅ ID: {prediction_id}")
                
                # Test 2: Endpoint de polling actuel
                print("\n🧪 Test 2: Endpoint de polling actuel...")
                test_polling_endpoint(prediction_id, headers)
                
                # Test 3: Endpoint alternatif
                print("\n🧪 Test 3: Endpoint alternatif...")
                test_alternative_endpoint(prediction_id, headers)
                
            else:
                print("❌ Pas d'ID")
                
        elif response.status_code == 401:
            print("❌ Erreur 401: Clé API invalide")
        elif response.status_code == 402:
            print("❌ Erreur 402: Quota épuisé")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_polling_endpoint(prediction_id: str, headers: dict):
    """Tester l'endpoint de polling actuel"""
    
    try:
        response = requests.get(
            f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text[:300]}...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_alternative_endpoint(prediction_id: str, headers: dict):
    """Tester un endpoint alternatif"""
    
    try:
        response = requests.get(
            f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text[:300]}...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 TEST ENDPOINTS WAVESPEED")
    print("=" * 40)
    test_wavespeed_endpoints() 