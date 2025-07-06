# Sử dụng một image Python ổn định làm base image
FROM python:3.9-slim-buster

# Thiết lập biến môi trường để Python không ghi các tệp .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy tệp requirements.txt và cài đặt các dependencies
# Đầu tiên copy và cài đặt dependencies để tận dụng Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt 
# Copy toàn bộ mã nguồn ứng dụng vào container

COPY . /app/

# Chạy lệnh collectstatic để thu thập các tệp tĩnh
# Các tệp này sẽ được Nginx phục vụ

# Lệnh mặc định để chạy ứng dụng bằng Gunicorn
# Sử dụng 0.0.0.0 để Gunicorn lắng nghe trên tất cả các interface mạng bên trong container
# --workers: Thường là (2 * số_lõi_CPU) + 1. Ví dụ: --workers 3
# --timeout: Thời gian tối đa worker chờ đợi trước khi bị kill (ví dụ: 120s)
# CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "3", "my_site.wsgi:application"]

ENV PORT=8080

#CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:${PORT} --workers 3 my_site.wsgi:application"]
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:${PORT} --workers 3 --timeout 120 --preload --log-level debug my_site.wsgi:application"]