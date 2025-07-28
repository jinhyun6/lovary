from pywebpush import generate_vapid_private_key, vapid_private_key_to_pem, vapid_public_key_to_bytes
import base64

# Generate VAPID keys
vapid_key = generate_vapid_private_key()
private_key_pem = vapid_private_key_to_pem(vapid_key.private_key)
public_key_bytes = vapid_public_key_to_bytes(vapid_key.public_key)
public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')

private_key_str = private_key_pem.decode('utf-8').replace('\n', '\\n')

print("Add these to your backend .env file:")
print(f"VAPID_PRIVATE_KEY={private_key_str}")
print(f"VAPID_PUBLIC_KEY={public_key_b64}")
print("\nAdd this to your frontend .env file:")
print(f"VITE_VAPID_PUBLIC_KEY={public_key_b64}")