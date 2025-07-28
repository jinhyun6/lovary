from pywebpush import webpush, WebPushException
import json
from app.core.config import settings

# VAPID keys should be generated once and stored in environment variables
# You can generate them using: 
# from pywebpush import generate_vapid_private_key
# vapid_key = generate_vapid_private_key()
# print(vapid_key.to_pem().decode())

VAPID_PRIVATE_KEY = getattr(settings, 'VAPID_PRIVATE_KEY', None)
VAPID_PUBLIC_KEY = getattr(settings, 'VAPID_PUBLIC_KEY', None)
VAPID_CLAIMS = {
    "sub": "mailto:your-email@example.com"
}

def send_push_notification(subscription_info: str, title: str, body: str, icon: str = "/icon-192x192.png"):
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        print("VAPID keys not configured")
        return False
    
    try:
        subscription = json.loads(subscription_info)
        
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": icon,
            "badge": "/icon-192x192.png"
        })
        
        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        return True
    except WebPushException as ex:
        print(f"Push notification failed: {ex}")
        return False
    except Exception as ex:
        print(f"Error sending push notification: {ex}")
        return False