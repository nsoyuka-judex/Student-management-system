import base64

def encrypt_text(text):
    # Simple base64 encoding as an example
    encrypted_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    return encrypted_text
def decrypt_text(encrypted_text):
    return base64.b64decode(encrypted_text).decode('utf-8')