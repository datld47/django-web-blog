from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,MinLengthValidator
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from zoneinfo import available_timezones

# Create your models here.

class PiMetricHistory(models.Model):
    """
    Lưu trữ dữ liệu lịch sử cho các metrics khác nhau của RaspberryPi (CPU, RAM, Nhiệt độ, Disk).
    """
    METRIC_TYPE_CHOICES = [
        ('CPU', 'CPU Usage'),
        ('RAM', 'RAM Usage (GB)'),
        ('DISK', 'Disk Space (GB)'),
        ('TEMP', 'CPU Temperature (C)'),
        # Bạn có thể thêm các loại metric khác nếu cần
    ]

    raspberry_pi = models.ForeignKey(
        'RaspberryPi',
        on_delete=models.CASCADE,
        related_name='metric_history', # Đổi related_name để phản ánh tính tổng quát
        help_text="Raspberry Pi mà bản ghi metric này thuộc về"
    )
    metric_type = models.CharField(
        max_length=10,
        choices=METRIC_TYPE_CHOICES,
        help_text="Loại metric (CPU, RAM, TEMP, DISK)"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, # Tự động đặt thời gian khi tạo bản ghi
        help_text="Thời gian ghi nhận metric"
    )
    value = models.FloatField( # Đổi tên từ cpu_percentage thành value
        help_text="Giá trị của metric tại thời điểm này"
    )

    class Meta:
        ordering = ['timestamp'] # Sắp xếp theo thời gian tăng dần
        verbose_name_plural = "Pi Metric Histories"
        # Đảm bảo không có trùng lặp cùng metric_type tại cùng timestamp cho cùng Pi
        unique_together = ('raspberry_pi', 'metric_type', 'timestamp') 

    def __str__(self):
        return (
            f"{self.get_metric_type_display()} for {self.raspberry_pi.pi_id} "
            f"- {self.value} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        )

class RaspberryPi(models.Model):
    
    pi_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100, help_text="Tên thân thiện của Raspberry Pi (ví dụ: Pi Khu Vực A)")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Vị trí vật lý của Pi")
    
    TIMEZONE_CHOICES = [(tz, tz) for tz in sorted(available_timezones())]
    
    timezone = models.CharField(
    max_length=50,
    choices=TIMEZONE_CHOICES,
    default='UTC',
    help_text="Múi giờ của Raspberry Pi, ví dụ: Asia/Ho_Chi_Minh")
    
    last_seen = models.DateTimeField(auto_now=True, help_text="Thời gian cuối cùng server nhận dữ liệu từ Pi này")
        # Trạng thái của Pi (ví dụ: 'online', 'offline', 'error')
    status = models.CharField(max_length=20, default='offline')
      # Địa chỉ IP nội bộ của Pi (có thể thay đổi nhưng hữu ích cho debug)
    local_ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    
    cpu_usage = models.FloatField(default=0.0, help_text="Mức sử dụng CPU hiện tại (%)")
    ram_usage_gb = models.FloatField(default=0.0, help_text="Mức sử dụng RAM hiện tại (GB)") # Hoặc ram_usage_percent
    disk_space_gb = models.FloatField(default=0.0, help_text="Dung lượng ổ đĩa còn trống (GB)") # Hoặc disk_space_percent
    cpu_temperature_celsius = models.FloatField(default=0.0, help_text="Nhiệt độ CPU hiện tại (°C)")
    
    def __str__(self):
        return f"{self.name} ({self.pi_id})"

    class Meta:
        verbose_name_plural = "Raspberry Pis"
    
    def is_online(self):
            """
            Xác định liệu Raspberry Pi có đang online hay không dựa vào last_seen.
            """
            if self.last_seen:
                online_threshold_seconds = 5 * 60 
                return (timezone.now() - self.last_seen).total_seconds() < online_threshold_seconds
            return False
        
class EspDevice(models.Model):
    """
    Đại diện cho một thiết bị ESP32 (vi xử lý) trong hệ thống.
    Mỗi ESP32 kết nối với một Raspberry Pi.
    """
    # ID duy nhất của ESP32 (ví dụ: MAC address, hoặc ID bạn gán)
    esp_id = models.CharField(max_length=100, unique=True, primary_key=True,
                              help_text="ID duy nhất của ESP32 (ví dụ: MAC address, hoặc ID do bạn gán)")
    
    # ESP32 này kết nối với Raspberry Pi nào
    raspberry_pi = models.ForeignKey('RaspberryPi', on_delete=models.CASCADE, 
                                     related_name='esp_devices', 
                                     help_text="Raspberry Pi mà ESP32 này kết nối tới")
    
    name = models.CharField(max_length=100, help_text="Tên thân thiện của ESP32 (ví dụ: ESP32 Phòng Khách)")
    
    location = models.CharField(max_length=200, blank=True, null=True, 
                                help_text="Vị trí vật lý của ESP32 (nếu khác với Pi)")
    
    # Giao thức mà Raspberry Pi sử dụng để giao tiếp với ESP32 này
    # Đây là giao thức giữa Pi và ESP32
    PROTOCOL_CHOICES_PI_ESP = [
        ('RS485', 'RS485 (Modbus/Custom)'),
        ('RS232', 'RS232 (Custom)'),
        ('WIFI', 'Wi-Fi (MQTT/ESP-NOW/HTTP)'),
        # Bạn có thể thêm các giao thức khác nếu cần
    ]
    communication_protocol_with_pi = models.CharField(max_length=20, 
                                                      choices=PROTOCOL_CHOICES_PI_ESP,
                                                      help_text="Giao thức Pi sử dụng để giao tiếp với ESP32 này")
    
    # Thời gian cuối cùng Pi nhận được dữ liệu/heartbeat từ ESP32 này
    last_seen = models.DateTimeField(auto_now=True, help_text="Thời gian cuối cùng Pi nhận dữ liệu/heartbeat từ ESP32 này")
    
    # Trạng thái của ESP32 (ví dụ: 'online', 'offline', 'error')
    status = models.CharField(max_length=20, default='offline')
    
    esp_firmware=models.CharField(max_length=200, blank=True, null=True, 
                                help_text="Phiên bản firmware")

    def __str__(self):
        return f"ESP32: {self.name} ({self.esp_id}) connected via {self.get_communication_protocol_with_pi_display()}"

    class Meta:
        verbose_name_plural = "ESP Devices"
          
class Sensor(models.Model):
    """
    Đại diện cho một cảm biến vật lý (ví dụ: nhiệt độ, độ ẩm) gắn vào một ESP32.
    """
    # Cảm biến này thuộc về ESP32 nào
    SENSOR_TYPE_CHOICES = [
        ('sound', 'SENSOR SOUND'),
        ('vibration', 'SENSOR VIBRATION'),
        ('temperature', 'SENSOR TEMPERATURE'),
        ('humidity', 'SENSOR HUMIDITY'),
    ]
    
    esp_device = models.ForeignKey(EspDevice, on_delete=models.CASCADE, 
                                    related_name='sensors', 
                                    help_text="ESP32 mà cảm biến này kết nối tới")
    
    # ID duy nhất của cảm biến trên ESP32 đó (ví dụ: địa chỉ I2C, số chân GPIO)
    sensor_id = models.CharField(max_length=100, 
                                 help_text="ID duy nhất của cảm biến (ví dụ: địa chỉ I2C, số chân GPIO trên ESP32)")
    
    name = models.CharField(max_length=100, help_text="Tên thân thiện của cảm biến (ví dụ: Cảm biến Nhiệt độ Phòng A)")
    
    
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPE_CHOICES, help_text="Loại cảm biến (ví dụ: 'temperature', 'humidity', 'light')") 
    
    
    UNIT_CHOICES = [
        ('°C', 'Độ C'),
        ('°F', 'Độ F'),
        ('%','% Độ ẩm'),
        ('mV','mV'),
        ('','Không rõ'),
    ]

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='',
        help_text="Đơn vị đo của cảm biến (người dùng có thể chọn)"
    )
    

    PROTOCOL_CHOICES_ESP_SENSOR = [
        ('I2C', 'I2C'),
        ('SPI', 'SPI'),
        ('ONEWIRE', 'OneWire'),
        ('ANALOG_PIN', 'Analog Pin'),
        ('DIGITAL_PIN', 'Digital Pin'),
        ('UART','UART')
    ]
    
    
    protocol_with_esp = models.CharField(max_length=20, choices=PROTOCOL_CHOICES_ESP_SENSOR,default='ANALOG_PIN',help_text="Giao thức ESP32 sử dụng để đọc cảm biến này")
       
    is_active = models.BooleanField(default=True, help_text="Cảm biến này có đang hoạt động không")
    

    def __str__(self):
        return f"{self.name} ({self.sensor_id}) on {self.esp_device.name}"
    
    class Meta:
        # Đảm bảo một ESP32 không có 2 cảm biến trùng ID
        unique_together = ('esp_device', 'sensor_id')
        
    def get_unit(self):
        return self.unit or {
            'temperature': '°C',
            'sound': 'mV',
            'vibration': 'mV',
            'humidity': '%'
        }.get(self.sensor_type, '')
        
    def get_type(self):
        return {
            'temperature': 'Cảm biến nhiệt',
            'sound': 'Cảm biến âm thanh',
            'vibration': 'Cảm biến rung',
            'humidity': 'Cảm biến độ ẩm không khí'
        }.get(self.sensor_type, '')

class SensorReading(models.Model):
    """
    Lưu trữ các giá trị đọc được từ một cảm biến cụ thể.
    """
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings',
                               help_text="Cảm biến tạo ra bản đọc này")
    
    # Thêm khóa ngoại đến EspDevice và RaspberryPi để dễ truy vấn hơn
    esp_device = models.ForeignKey(EspDevice, on_delete=models.CASCADE, related_name='all_sensor_readings',
                                   help_text="ESP32 mà cảm biến này gắn vào")
    
    raspberry_pi = models.ForeignKey(RaspberryPi, on_delete=models.CASCADE, related_name='all_esp_sensor_readings',
                                     help_text="Raspberry Pi mà ESP32 này kết nối tới")
    
    value = models.FloatField(help_text="Giá trị đọc được từ cảm biến")
    
    # Thời gian đọc được ghi nhận TẠI THIẾT BỊ (ESP32/Sensor)
    timestamp_device = models.DateTimeField(help_text="Thời gian đọc được ghi nhận tại thiết bị cảm biến/ESP32") 
    
    # Thời gian dữ liệu được nhận tại server (do Django tự động thêm)
    timestamp_server = models.DateTimeField(auto_now_add=True, 
                                            help_text="Thời gian dữ liệu được nhận tại Django Server") 

    class Meta:
        ordering = ['-timestamp_device'] # Sắp xếp theo thời gian mới nhất
        # Đảm bảo không trùng lặp dữ liệu: cùng một cảm biến, cùng một thời điểm đọc tại thiết bị
        unique_together = ('sensor', 'timestamp_device') 
        verbose_name_plural = "Sensor Readings"

    def __str__(self):
        return f"{self.sensor.name}: {self.value} at {self.timestamp_device} (via {self.esp_device.name})"

class SensorTemperatureConfig(models.Model):
    
    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        related_name='temperature_config',
        limit_choices_to={'sensor_type': 'temperature'},
        help_text="Chỉ áp dụng cho cảm biến nhiệt độ"
    )
    
    read_interval_seconds = models.PositiveIntegerField(
        default=300,  # tương đương 5 phút
        help_text="Chu kỳ đọc dữ liệu (giây)"
    )
    
    threshold_high = models.FloatField(
        default=50.0,
        help_text="Ngưỡng cảnh báo cao (°C)"
    )
    threshold_low = models.FloatField(
        default=10.0,
        help_text="Ngưỡng cảnh báo thấp (°C)"
    )

    def __str__(self):
        return f"Cấu hình nhiệt độ cho {self.sensor.name}"

class SensorSoundConfig(models.Model):
    
    sensor = models.OneToOneField(
        Sensor, 
        on_delete=models.CASCADE, 
        related_name='sound_config',
        limit_choices_to={'sensor_type': 'sound'},
        help_text="Chỉ áp dụng cho cảm biến âm thanh"
    )
    # Cải tiến: Sử dụng IntegerField với choices cho gain
    class GainChoices(models.IntegerChoices):
        GAIN_25X = 25, "25x Gain"
        GAIN_60X = 60, "60x Gain"
        GAIN_125X = 125, "125x Gain"
        
    gain_multiplier = models.IntegerField(
        choices=GainChoices.choices,
        default=GainChoices.GAIN_60X,
        help_text="Hệ số khuếch đại tín hiệu âm thanh (ví dụ: 25, 60, 125)."
    )

    sampling_interval_ms = models.PositiveIntegerField(default=100, help_text="Thời gian lấy mẫu ADC của vi điều khiển (mili giây).") # Rõ ràng hơn

    sound_threshold_mv = models.FloatField(default=300.0, help_text="Ngưỡng điện áp analog (mV) từ cảm biến để phát hiện sự kiện âm thanh.")

    hold_time_ms = models.PositiveIntegerField(default=500, help_text="Thời gian tối thiểu (ms) âm thanh phải vượt ngưỡng để kích hoạt sự kiện.") # Thêm help_text

    read_interval_seconds = models.PositiveIntegerField(default=60, help_text="Chu kỳ gửi dữ liệu định kỳ về server (giây), bất kể có sự kiện.") # Thêm help_text

    class OperatingMode(models.TextChoices):
        CONTINUOUS = 'CONTINUOUS', 'Liên tục (gửi định kỳ)'
        EVENT_TRIGGERED = 'EVENT_TRIGGERED', 'Kích hoạt sự kiện (chỉ gửi khi vượt ngưỡng)'
        HYBRID = 'HYBRID', 'Kết hợp (định kỳ & sự kiện)'

    operating_mode = models.CharField(
        max_length=20,
        choices=OperatingMode.choices,
        default=OperatingMode.CONTINUOUS,
        help_text="Chế độ hoạt động của cảm biến (liên tục, sự kiện, kết hợp)."
    )

    def __str__(self):
        return f"Sound Config for {self.sensor.name}"

class SensorVibrationConfig(models.Model):
    """
    Bảng cấu hình cụ thể cho cảm biến rung động.
    """
    sensor = models.OneToOneField(
        'Sensor', # Thay thế bằng tên model Sensor của bạn nếu nó ở module khác
        on_delete=models.CASCADE,
        related_name='vibration_config',
        limit_choices_to={'sensor_type': 'vibration'},
        help_text="Chỉ áp dụng cho cảm biến rung động"
    )

    vibration_threshold_mv = models.FloatField(
        default=500.0, # Giá trị ví dụ, cần hiệu chỉnh thực tế
        help_text="Ngưỡng phát hiện rung động. Nếu là analog, là giá trị ADC. Nếu là digital, là ngưỡng logic."
    )

    # 2. Thời gian trễ (debounce time) để tránh rung động giả
    debounce_time_ms = models.PositiveIntegerField(
        default=100,
        help_text="Thời gian tối thiểu (ms) giữa hai lần phát hiện rung động liên tiếp để tránh nhiễu."
    )
    
    sampling_interval_ms = models.PositiveIntegerField(default=100, help_text="Thời gian lấy mẫu ADC của vi điều khiển (mili giây).") # Rõ ràng hơn
    
    # 3. Chế độ hoạt động (tương tự SoundConfig)
    class OperatingMode(models.TextChoices):
        CONTINUOUS = 'CONTINUOUS', 'Liên tục (gửi định kỳ cường độ)'
        EVENT_TRIGGERED = 'EVENT_TRIGGERED', 'Kích hoạt sự kiện (chỉ gửi khi vượt ngưỡng)'
        HYBRID = 'HYBRID', 'Kết hợp (định kỳ & sự kiện)'

    operating_mode = models.CharField(
        max_length=20,
        choices=OperatingMode.choices,
        default=OperatingMode.CONTINUOUS, # Rung động thường quan tâm sự kiện hơn
        help_text="Chế độ hoạt động của cảm biến rung."
    )
    
    read_interval_seconds = models.PositiveIntegerField(
        default=60,
        help_text="Chu kỳ gửi dữ liệu định kỳ về server (giây), áp dụng ở chế độ liên tục/kết hợp."
    )

    def __str__(self):
        return f"Cấu hình rung động cho {self.sensor.name}"



# class Alarm(models.Model):
#     # Liên kết với thiết bị gây ra cảnh báo
#     # Một cảnh báo có thể đến từ Sensor, ESP, hoặc RaspberryPi
#     # Sử dụng GenericForeignKey nếu cảnh báo có thể đến từ nhiều loại model
#     # Hoặc đơn giản hơn là các ForeignKeys riêng biệt nếu chỉ có vài loại
#     sensor = models.ForeignKey('Sensor', on_delete=models.SET_NULL, null=True, blank=True, related_name='alarms')
#     esp_device = models.ForeignKey('EspDevice', on_delete=models.SET_NULL, null=True, blank=True, related_name='alarms')
#     raspberry_pi = models.ForeignKey('RaspberryPi', on_delete=models.SET_NULL, null=True, blank=True, related_name='alarms')

#     ALARM_TYPE_CHOICES = [
#         ('OVER_THRESHOLD', 'Vượt ngưỡng cảm biến'),
#         ('OFFLINE', 'Thiết bị offline'), # Cảnh báo nếu thiết bị offline quá lâu
#         ('HIGH_CPU', 'CPU quá tải'),
#         ('LOW_DISK', 'Đĩa đầy'),
#         ('SENSOR_ERROR', 'Cảm biến lỗi'),
#         # ... thêm các loại cảnh báo khác
#     ]
#     alarm_type = models.CharField(max_length=50, choices=ALARM_TYPE_CHOICES, help_text="Loại cảnh báo")
    
#     message = models.TextField(help_text="Mô tả chi tiết cảnh báo")
#     triggered_value = models.FloatField(null=True, blank=True, help_text="Giá trị gây ra cảnh báo (nếu có)")
    
#     triggered_at = models.DateTimeField(auto_now_add=True, help_text="Thời gian cảnh báo được kích hoạt")
    
#     is_active = models.BooleanField(default=True, help_text="Cảnh báo này có đang hoạt động (chưa được xử lý) không?")
#     acknowledged_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian cảnh báo được xác nhận")
#     acknowledged_by = models.ForeignKey(
#         'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alarms'
#     )

#     def __str__(self):
#         return f"[{'ACTIVE' if self.is_active else 'RESOLVED'}] {self.alarm_type} - {self.message}"

#     class Meta:
#         ordering = ['-triggered_at']