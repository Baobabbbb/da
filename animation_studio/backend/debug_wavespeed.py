#!/usr/bin/env python3
"""
Debug Wavespeed - voir exactement ce qui est retourné
"""

import requests
import time
import os
from dotenv import load_dotenv

def debug_wavespeed():
    """Debug complet de Wavespeed"""
    
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
    
    print("🧪 Test complet Wavespeed...")
    
    try:
        # 1. Appel initial
        response = requests.post(
            "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prediction_id = result.get("data", {}).get("id") or result.get("id")
            
            if prediction_id:
                print(f"✅ ID: {prediction_id}")
                
                # 2. Polling avec debug complet
                debug_polling(prediction_id, headers)
                
            else:
                print("❌ Pas d'ID")
                
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def debug_polling(prediction_id: str, headers: dict):
    """Debug du polling avec affichage complet"""
    
    print(f"🔄 Polling pour {prediction_id}...")
    
    for attempt in range(10):  # Test rapide
        try:
            print(f"\n🔄 Tentative {attempt+1}/10...")
            
            response = requests.get(
                f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📝 Réponse complète: {result}")
                
                # Extraire le status
                status = result.get("data", {}).get("status", "unknown")
                print(f"📈 Status: {status}")
                
                if status == "completed":
                    # Debug des outputs
                    outputs = result.get("data", {}).get("outputs", [])
                    print(f"🔍 Outputs: {outputs}")
                    print(f"🔍 Type outputs: {type(outputs)}")
                    
                    if outputs and len(outputs) > 0:
                        print(f"🔍 Outputs[0]: {outputs[0]}")
                        print(f"🔍 Type outputs[0]: {type(outputs[0])}")
                        
                        # Test sécurisé
                        try:
                            if isinstance(outputs[0], str):
                                print(f"✅ Outputs[0] est une chaîne: {outputs[0]}")
                            elif isinstance(outputs[0], dict):
                                print(f"✅ Outputs[0] est un dict: {outputs[0]}")
                                url = outputs[0].get("url")
                                print(f"🔗 URL extraite: {url}")
                            else:
                                print(f"⚠️  Type inattendu: {type(outputs[0])}")
                        except Exception as e:
                            print(f"❌ Erreur lors du test: {e}")
                    
                    return
                    
                elif status == "failed":
                    print(f"❌ Échec: {result}")
                    return
                    
                elif status in ["processing", "queued", "starting"]:
                    print(f"⏳ En cours... ({status})")
                    
            else:
                print(f"⚠️  Status: {response.status_code}")
                
            time.sleep(5)
            
        except Exception as e:
            print(f"⚠️  Erreur: {e}")
            time.sleep(5)
    
    print("⏰ Timeout debug")

if __name__ == "__main__":
    print("🚀 DEBUG WAVESPEED")
    print("=" * 40)
    debug_wavespeed() 