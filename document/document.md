# Xây dựng từ docker file

-  **docker file** -> docker image -> docker container

```
#docker file cho django project

# Sử dụng một image Python ổn định làm base image
FROM python:3.9-slim-buster

# Thiết lập biến môi trường để Python không ghi các tệp .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy tệp requirements.txt và cài đặt các dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt 

# Copy toàn bộ mã nguồn ứng dụng vào container
COPY . /app/

# thiết lập cổng cho docker container
ENV PORT=8080

# Lệnh mặc định để chạy ứng dụng bằng Gunicorn
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:${PORT} --workers 3 my_site.wsgi:application"]

```

```
#docker fle cho flask project

# Sử dụng image Python 3.11 nền tảng nhẹ (slim-buster)
FROM python:3.11-slim-buster

# Đặt thư mục làm việc bên trong container là /app
WORKDIR /app

# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các thư viện Python từ requirements.txt
# --no-cache-dir: Giảm kích thước image bằng cách không lưu cache pip
# Bạn có thể thêm --upgrade pip ở đây nếu muốn pip mới nhất trong image
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của ứng dụng (bao gồm app.py) vào thư mục làm việc
COPY . .

# Đặt biến môi trường PORT mà ứng dụng sẽ lắng nghe
# Gunicorn sẽ sử dụng biến này. Cloud Run cũng sẽ cung cấp biến PORT.
ENV PORT=8080 

# Lệnh để chạy ứng dụng của bạn khi container khởi động
# Sử dụng Gunicorn (một WSGI server sản phẩm) để chạy ứng dụng Flask
# --bind 0.0.0.0:${PORT}: Lắng nghe trên tất cả các địa chỉ IP nội bộ tại cổng ${PORT}
# app:app: Tên module Python (app.py) và tên biến Flask instance (ví dụ: app = Flask(__name__))

CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:${PORT} app:app"]

```
`
**gunicorn**
- **Kiến trúc máy chủ web**
request -> Máy chủ web/reverse proxy : Ngix hoặc Apache->**Máy chủ ứng dụng: gunicorn** -> Ứng dụng python: flask , django...

- Ngix hoặc Apache: 
	- Phục vụ file tĩnh  css
	- Chứng thực ssl
	- Chuyển tiếp đến máy chủ ứng dụng gunicorn
	  
- **Máy chủ ứng dụng gunicorn**
	- Gunicorn nhận các yêu cầu động từ Nginx/Apache.
	- Nó quản lý các worker process để xử lý các yêu cầu HTTP đồng thời
	- Giao tiếp với ứng dụng Python của bạn thông qua giao thức WSGI.(Web Server Gateway Interface)
 
  
- docker file ->**docker image** -> docker container

### Build docker image

  - Môi trường  decktop - docker
  - 
````
docker build -t <tên-image>:<tag> <đường-dẫn-đến-Dockerfile>
````

````
#xây dựng image lên docker desktop

docker build -t my-app-test:lastest .

````
 
  - Môi trường  cloud run
````
#xây dựng image lên docker desktop

docker build -t us-central1-docker.pkg.dev/gemini-18-460419/cloud-run-source-deploy/my-django-app:latest .

#Đẩy image xay dựng lên clound

docker push us-central1-docker.pkg.dev/gemini-18-460419/cloud-run-source-deploy/my-django-app:latest
````

### Biến môi trường
- Hầu như ứng dụng xây dựng từ docker file cần cung cấp một biến môi trường
  
#### Biên mối trường  cho docker-destop : flle .env
```
# Production settings
DJANGO_DEBUG=True
SETTING_DEFAUT=False
SECRET_KEY_PROD=ZGphbmdvLWluc2VjdXJlLW09cUAjZF8hJTcwdCYkaDY2dmtqYyZzZjMxNjVnMzQpKDImaiQtPShvKjIzYXZqdDd4
APP_HOST=localhost,127.0.0.1
TRUSTED_CSRF_APP_HOST=http://localhost:8000,http://127.0.0.1:8000
PORT=8080
POSTGRES_DB=mydjangodb
POSTGRES_USER=dat
POSTGRES_PASSWORD=111111
POSTGRES_HOST=34.133.203.78
POSTGRES_PORT=5432
GS_BUCKET_NAME=my-django-app-static-media-dat
GOOGLE_APPLICATION_CREDENTIALS=gcp-sa-key.json
````

- trong file .env  phải viết liền: Ở đây SECRECT_KEY_PRO phức tạo nên đã chuyển sang base64 cho hợp lệ
````
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
````


- Trong này chứa các thông tin cố định và được gọi thông qua: `os.getenv()`
````
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_site.settings')

````

- Biến môi trường cho cloud run được cấu hình dựa bảng sau trong quá trình triển khai container
  ![a4832fdd0f467743aedf51cea9d83e85.png](:/f1cd7549e09c46d797fbfc17f0b668cf)

### Triển khai container:
Cần 2 thông tin sau:
- docker image
- thông tin biến môi trường (cho cloud run)  hoặc file  .env  (cho desktop-docker)
  
#### Triển khai trên môi trườn decktop-docker
```
docker run -d --env-file .env -p <cổng_host>:<cổng_container> --name <tên_container> <tên_image>:<tag>
````

```
docker run -d --env-file .env -p 8000:8080 --name my-app-test-container my-app-test:lastest
````

#### Triển khai trên môi trường cloud run
- Triển khai bằng giao diện và chú ý các khóa bí mật nên triển khai trong khu vực hình bên dưới nó được quản lý bởi dịch vụ
secrect management
  ![3935ee3f6a7ed7b444b555da326323f2.png](:/2429a247897a4766b5ff833f1f8c5834)

  ![645a0b4f1deef112b367d9783491e4a3.png](:/c6c86986f4f94e289aa1af7921c35597)

---
### Triển khai static file:
- Static file cần một máy chủ để phục vụ cho việc load các css.
- Triển khai static file  bằng dịch vụ  bucket của google cloud storge (GCS): 
 ![54e4d75f00dcab769ee636895853f30e.png](:/1f396dad074745379cb6e3d48e1061d0)
- Liên kết ứng dụng với GCS
  ````
      GS_QUERYSTRING_AUTH = False

    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME','my-django-app-static-media-dat')
    GS_STATIC_LOCATION = 'static' # Thư mục trong bucket cho static files
    GS_MEDIA_LOCATION = 'media'   # Thư mục trong bucket cho media files

    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR,  os.getenv('GOOGLE_APPLICATION_CREDENTIALS','gcp-sa-key.json'))
    )

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": GS_BUCKET_NAME,
                "location": "media",
                "default_acl": "publicRead",
                "credentials": GS_CREDENTIALS,
                "querystring_auth": False,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": GS_BUCKET_NAME,
                "location": "static",
                "default_acl": "publicRead",
                "credentials": GS_CREDENTIALS,
                "querystring_auth": False,
            },
        },
    }

    STATIC_ROOT = BASE_DIR / "staticfiles" # Vẫn cần cho collectstatic cục bộ
    MEDIA_ROOT = BASE_DIR / "uploads"      # Vẫn cần cho tải lên tạm thời trước khi đẩy lên GCS

    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_STATIC_LOCATION}/"
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_MEDIA_LOCATION}/"
  ````

  - STATIC_URL  và MEDIA_URL   là 2 địa chỉ để truy cập vào bucket ( mỗi bucket đại diện bởi tên)
  - STATIC ROOT và MEDIA_ROOT  sẽ là bộ nhớ tạm lưu trữ và sẽ được đẩy lên bucket  nhờ vào thư viện `storage`
 
  ### Triển khai databse
- Databse phục vụ lưu trữ dữ liệu lâu dài
````
	    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql', # Sử dụng PostgreSQL
            'NAME': os.getenv('POSTGRES_DB','mydjangodb'),
            'USER': os.getenv('POSTGRES_USER','dat'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD','111111'),
            'HOST': os.getenv('POSTGRES_HOST', '34.133.203.78'), 
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
````

- Ở trên là cấu hình database postgest, với các thông số được thiết lập ở biến môi trường
- Database được chạy trên một máy chủ linux  riêng hoặc thông qua dịch vụ VM instant của google
![a30cfb8ebb448b68cdb7c4cfbb9d27b3.png](:/643d293876254d4a87bd1a36dbc33fd1)
- Khi triên khai trên VM instant cần phải thiết lập tường lửa cho phép dịch vụ đi vào
![ac09874b882145d0c176074514d2feb4.png](:/bcf8fae35ec9405fa7428dcd8b6cf520)
  
![0f1e3bc8df6aba0ad59faac52bf117fa.png](:/2b3bb689b2d3461ab0a6e4fd6870c249)

### Cách thưc để đồng bộ dữ liệu lên GCS và  lên databse 
- Chuyển dữ liệu vào  GCS
  - Khai báo vị trí static file
````
STATICFILES_DIRS=[
        BASE_DIR / "static"
    ]
````
 
 -  Gom static file và chuyển lên bucket
 -  
  ```
  python manage.py collectstatic --noinput --verbosity 2

  ````

- chuyển dữ liệu vào databse:
````  
python manage.py makemigrations             # cập nhập model

python manage.py migrate                    # đẩy dữ liệu lên databse

````

***Vơi postgest databse cần thư viện `psycopg2-binary` mới migrate được

---
### Xây dựng tất cả : ứng dụng web, static flile ,  database trên một máy chủ linux
- Cần một máy chủ linux  trên đó triển khai các dịch vụ : gunicorn, Ngix , databse, ứng dụng app
- `dockerfile` xem ở trên
  
- Để làm điều này ta cần kết hợp docker với file `docker-compose.yml`
````
version: '3.8'

services:
  web:
    # Build context là thư mục hiện tại (DJANGO-TRAINING/)
    build: .
    command: gunicorn --bind 0.0.0.0:${PORT}  --workers 3 my_site.wsgi:application
    expose:
      - ${PORT}
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      # Gắn static_volume vào thư mục STATIC_ROOT của Django trong web container
      # Đây là nơi collectstatic đã ghi các tệp tĩnh
      - static_volume:/app/staticfiles
      # Gắn media_volume vào thư mục MEDIA_ROOT của Django trong web container
      # Đây là nơi Django sẽ ghi các tệp do người dùng upload
      - media_volume:/app/uploads
    # ----------------------------------

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      # Nginx config nằm trong thư mục nginx/ ở cấp hiện tại
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      # Volume ánh xạ đến STATIC_ROOT và MEDIA_ROOT
      # Đảm bảo đường dẫn này khớp với cấu hình trong settings.py và collectstatic
      - static_volume:/vol/static  # Nơi Nginx tìm static files
      - media_volume:/vol/media    # Nơi Nginx tìm media files
    depends_on:
      - web
  db:
    image: postgres:13-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env

volumes:
  postgres_data:
  static_volume:
  media_volume:

````

- Với cấu hình trên ta cấu hình máy chủ như sau:
  - Ta khai báo 3 ổ đĩa :  postgres_data, static_volume, media_volume: 3 ổ đĩa này nằm ngoài container
  - Ta thực hiện mount  STATIC_ROOT: /app/staticfiles  và  MEDIA_ROOT:  /app/uploads  vào ổ đĩa static_volume và media_volume
  - Ta thực hiện mount  database postgest : thư mục  /var/lib/postgresql/data/   vào ổ đĩa postgres_data
  - Với Nginx ta cũng mount  thưc mục  /vol/static   và  /vol/media  vào ổ đĩa static_volume và media_volume
  - Ta liên kết file .env vào ứng dụng
  - Liên kết database  db vào ứng dụng
  - Cấu hình ngix để thực hiện chuyển tiếp: được khai báo trong file: ./nginx/default.conf  sẽ được map vào container tại
    /etc/nginx/conf.d/default.conf

```
  upstream django {
    server web:8080;
}

server {
    listen 80;
    server_name localhost 127.0.0.1;

    # Phục vụ static files từ volume được gắn
    location /static/ {
        alias /vol/static/;
    }

    # Phục vụ media files từ volume được gắn
    location /files/ {
        alias /vol/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
````

- Ở đây tất cả đều qua máy chủ nginx  trước: Máy chủ luôn lắng nghe ở địa chỉ  127.0.0.1:80  và đã cấu hình port forward: 80:80 .  
-  Nếu yêu cầu static  hoặc files  thì sẽ lấy ngay . Còn cái khác sẽ chuyển tiếp đến địa chỉ   web:8080  đến máy chủ gunicorn đang lắng nghe trên port này  để xử lý

- file  `.env`
````
DJANGO_DEBUG=True
SETTING_DEFAUT=False
SECRET_KEY_PROD=ZGphbmdvLWluc2VjdXJlLW09cUAjZF8hJTcwdCYkaDY2dmtqYyZzZjMxNjVnMzQpKDImaiQtPShvKjIzYXZqdDd4
APP_HOST=localhost,127.0.0.1
TRUSTED_CSRF_APP_HOST=http://localhost:8000,http://127.0.0.1:8000
PORT=8080
POSTGRES_DB=mydjangodb
POSTGRES_USER=dat
POSTGRES_PASSWORD=111111
POSTGRES_HOST=db
POSTGRES_PORT=5432
````

## Thực hiện build image  và  container

```
docker-compose build
docker-compose up -d db
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
docker-compose run --rm web python manage.py collectstatic --noinput    
docker-compose up -d
docker-compose ps

```

-  Ta build  ứng dụng trước (web)
-  Tiếp đên build  database:  lệnh này sẽ kéo databse postgest  về và cài
-  sau đó thực hiện  đồng bộ database,  tạo tài khoản admin
-  sau đó tổng họp static file
-  tiếp đến sẽ run các dịch vụ còn lại
-  Kiểm tra các dịch vụ đang chạy


```
Một số lệnh điều khiển
docker-compose down -v   \\dừng container  và xóa  volume

docker-compose logs -f web   \\hiện log web

docker-compose logs -f nginx  \\hiện log nginx

````
