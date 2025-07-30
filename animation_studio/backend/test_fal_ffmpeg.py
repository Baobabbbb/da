import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

FAL_API_KEY = os.getenv("FAL_API_KEY")

def test_fal_ffmpeg():
    """Test simple de l'API FAL FFmpeg"""
    print("🧪 Test de l'API FAL FFmpeg...")
    
    # Payload simple pour test
    payload = {
        "tracks": [
            {
                "id": "1",
                "type": "video",
                "keyframes": [
                    {
                        "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                        "timestamp": 0,
                        "duration": 10
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Payload envoyé: {payload}")
    print(f"🔑 Clé API: {FAL_API_KEY[:10]}...")
    
    try:
        response = requests.post(
            "https://queue.fal.run/fal-ai/ffmpeg-api/compose",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Réponse: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            request_id = result.get("request_id") or result.get("id")
            print(f"🆔 Request ID: {request_id}")
            
            # Polling pour voir le statut
            for i in range(10):
                print(f"🔄 Polling {i+1}/10...")
                time.sleep(3)
                
                poll_response = requests.get(
                    f"https://queue.fal.run/fal-ai/ffmpeg-api/requests/{request_id}",
                    headers=headers,
                    timeout=30
                )
                
                if poll_response.status_code == 200:
                    poll_result = poll_response.json()
                    print(f"📊 Status: {poll_result.get('status')}")
                    print(f"📊 Résultat complet: {poll_result}")
                else:
                    print(f"❌ Erreur polling: {poll_response.status_code} - {poll_response.text}")
        else:
            print(f"❌ Erreur initiale: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_fal_ffmpeg() 