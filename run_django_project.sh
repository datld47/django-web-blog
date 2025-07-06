#!/bin/bash

# 1. Kích hoạt môi trường ảo (từ vị trí hiện tại của script)
echo "Kich hoat moi truong ao: ./myenv"
if [ -f "./myenv/Scripts/activate" ]; then
    source "./myenv/Scripts/activate"
else
    echo "Loi: File kich hoat moi truong ao khong ton tai tai ./myenv/bin/activate."
    echo "Kiem tra ten thu muc moi truong ao (myenv/venv)."
    exit 1
fi

# 2. Điều hướng đến thư mục gốc của dự án Django (từ vị trí hiện tại của script)
echo "Chuyen thu muc den: ./django_project"
cd "./django_project" || { echo "Loi: Khong the chuyen thu muc den ./django_project. Kiem tra ten thu muc du an."; exit 1; }


# 3. Chạy Django Development Server
echo "Khoi dong Django Development Server..."
echo "Server se chay tren http://127.0.0.1:8000/tutor/hello/"
echo "Nhan Ctrl+C de dung server."

# Luôn chạy lệnh này cuối cùng
python manage.py runserver 0.0.0.0:8000

# Giữ cửa sổ terminal mở sau khi server dừng (chỉ khi script kết thúc)
# read -p "Nhan mot phim bat ky de dong cua so..." -n 1
#