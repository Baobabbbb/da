#!/usr/bin/env python3
"""
Script de diagnostic pour tester l'API Wavespeed
"""

import requests
import time
import os
from dotenv import load_dotenv

def test_wavespeed():
    """Test direct de l'API Wavespeed"""
    
    load_dotenv()
    WAVESPEED_API_KEY = os.getenv('WAVESPEED_API_KEY')
    
    if not WAVESPEED_API_KEY:
        print("❌ Clé API Wavespeed manquante")
        return False
    
    print(f"🔑 Clé API Wavespeed: {WAVESPEED_API_KEY[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "aspect_ratio": "9:16",
        "duration": 10,
        "prompt": "2D cartoon animation, Disney style, simple test animation, vibrant colors"
    }
    
    print("🧪 Test 1: Appel initial Wavespeed...")
    
    try:
        # Test 1: Appel initial
        start_time = time.time()
        response = requests.post(
            "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
            headers=headers,
            json=data,
            timeout=30
        )
        
        call_time = time.time() - start_time
        print(f"⏱️  Temps d'appel initial: {call_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            result = response.json()
            prediction_id = result.get("data", {}).get("id") or result.get("id")
            
            if prediction_id:
                print(f"✅ ID de prédiction obtenu: {prediction_id}")
                
                # Test 2: Polling rapide
                print("\n🧪 Test 2: Polling résultat...")
                return test_polling(prediction_id, headers)
            else:
                print("❌ Pas d'ID de prédiction dans la réponse")
                return False
                
        elif response.status_code == 401:
            print("❌ Erreur 401: Clé API invalide")
            return False
        elif response.status_code == 402:
            print("❌ Erreur 402: Quota épuisé")
            return False
        elif response.status_code == 404:
            print("❌ Erreur 404: Endpoint incorrect")
            return False
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de l'appel initial (30s)")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_polling(prediction_id: str, headers: dict):
    """Test du polling avec timeout réaliste"""
    
    print(f"🔄 Polling pour {prediction_id}...")
    start_time = time.time()
    
    for attempt in range(84):  # 7 minutes max (84 * 5s = 420s = 7min)
        try:
            elapsed = time.time() - start_time
            print(f"🔄 Tentative {attempt+1}/84 - Elapsed: {elapsed:.1f}s")
            
            response = requests.get(
                f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                print(f"📈 Status: {status}")
                
                if status == "completed":
                    video_url = result.get("output", {}).get("video_url") or result.get("output")
                    if video_url:
                        total_time = time.time() - start_time
                        print(f"✅ SUCCÈS! Vidéo générée en {total_time:.1f}s")
                        print(f"🎬 URL: {video_url[:50]}...")
                        return True
                    else:
                        print("❌ Pas d'URL vidéo dans la réponse")
                        return False
                        
                elif status == "failed":
                    print("❌ Génération échouée")
                    print(f"🔍 Détails: {result}")
                    return False
                    
                elif status in ["processing", "queued", "starting"]:
                    print(f"⏳ En cours... ({status})")
                    
            else:
                print(f"⚠️  Status polling: {response.status_code}")
                
            if elapsed > 420:  # Plus de 7 minutes
                print("❌ TIMEOUT: Plus de 7 minutes - Anormal!")
                return False
                
            time.sleep(5)
            
        except Exception as e:
            print(f"⚠️  Erreur polling: {e}")
            time.sleep(5)
    
    print("❌ TIMEOUT: Génération trop longue (>7min)")
    return False

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC WAVESPEED")
    print("=" * 40)
    
    success = test_wavespeed()
    
    if success:
        print("\n✅ DIAGNOSTIC: Wavespeed fonctionne normalement")
    else:
        print("\n❌ DIAGNOSTIC: Problème détecté avec Wavespeed") 