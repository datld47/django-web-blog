import base64
import os
DJANGO_SECRET_KEY = "django-insecure-m=q@#d_!%70t&$h66vkjc&sf3165g34)(2&j$-=(o*23avjt7x"
def generate_base64_secret_key(key_string: str) -> str:
    encoded_bytes = base64.b64encode(key_string.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

if __name__ == "__main__":
    if not DJANGO_SECRET_KEY:
        print("Lỗi: Vui lòng đặt khóa bí mật Django của bạn vào biến DJANGO_SECRET_KEY trong script này.")
    else:
        encoded_key = generate_base64_secret_key(DJANGO_SECRET_KEY)
        print("Khóa bí mật Django gốc của bạn:")
        print(f"  {DJANGO_SECRET_KEY}")
        print("---\n")
        print("Khóa bí mật đã mã hóa Base64 (dùng cho file .env):")
        print(f"  {encoded_key}")
