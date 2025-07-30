from datetime import date
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.shortcuts import render,get_object_or_404
from django.template.loader import render_to_string 
from django.views.generic import ListView,DetailView
from django.views import View
from django.views.decorators.csrf import csrf_exempt # Cần thiết cho API từ thiết bị
from django.utils.decorators import method_decorator
import json 
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime
from pytz import timezone as pytz_timezone 

from django.utils.dateparse import parse_datetime
from collections import defaultdict
from django.db.models import Prefetch, Count, Sum, OuterRef, Subquery, CharField,FloatField,DateTimeField,Q

from .models import RaspberryPi,EspDevice,Sensor,SensorReading,PiMetricHistory,SensorTemperatureConfig,SensorVibrationConfig
import re
from .forms import SensorTemperatureConfigForm,SensorSoundConfigForm,SensorVibrationConfigForm

#----------------------------------------function---------------------------------------#

def get_tree_data_for_jstree():
    """
    Hàm này sẽ lấy dữ liệu từ các model Django và định dạng lại cho jsTree.
    """
    jstree_nodes = []    

    # 1. Thêm các Raspberry Pi (Root Nodes)
    pis = RaspberryPi.objects.all().prefetch_related('esp_devices') # Tối ưu truy vấn
    for pi in pis:
        # Mỗi Pi là một node gốc.
        # Chúng ta có thể thêm status vào text, hoặc dùng type để thay đổi icon
        rendered_html_text = render_to_string(
                    'iot_app/partials/tree_node/raspi_node_content.html',
                    {'pi': pi} # Truyền đối tượng sensor vào context của partial template
                )

        jstree_nodes.append({
            "id": f"{pi.pi_id}", # ID node trong jsTree
            "parent": "#",         # Là node gốc
            "text": rendered_html_text,
            "type": "raspberry_pi", # Để có thể tùy chỉnh icon/style cho Pi
            "state": { "opened": True } # Mở Pi mặc định để thấy các thiết bị con
        })

        # 2. Thêm các ESP Devices (Children of Raspberry Pi)
        esp_devices = pi.esp_devices.all().prefetch_related('sensors') # Tối ưu truy vấn
        for esp in esp_devices:
            
            rendered_html_text = render_to_string(
                    'iot_app/partials/tree_node/esp_node_content.html',
                    {'esp': esp} # Truyền đối tượng sensor vào context của partial template
                )
            jstree_nodes.append({
                "id": f"{esp.esp_id}",
                "parent": f"{pi.pi_id}", # Parent là Pi
                "text": rendered_html_text,
                "type": "esp_device", # Để tùy chỉnh icon/style cho ESP
                "state": { "opened": False } # Mở theo nhu cầu
            })

            # 3. Thêm các Sensor (Children of ESP Device)
            #sensors = esp.sensors.all()
            
            latest_value_subquery = SensorReading.objects.filter(sensor=OuterRef('pk')).order_by('-timestamp_device').values('value')[:1]
            
            latest_time_subquery = SensorReading.objects.filter(sensor=OuterRef('pk')).order_by('-timestamp_device').values('timestamp_device')[:1]

            sensors = esp.sensors.annotate(
                
                latest_value=Subquery(latest_value_subquery, output_field=CharField()),
                latest_date=Subquery(latest_time_subquery, output_field=DateTimeField())
            )
            
            for sensor in sensors:
                
                # latest_reading = sensor.readings.order_by('-timestamp_device').first()
                # sensor.latest_value = latest_reading.value if latest_reading else 'N/A'
                # sensor.latest_timestamp_device = latest_reading.timestamp_device if latest_reading else None       
                rendered_html_text = render_to_string(
                    'iot_app/partials/tree_node/sensor_node_content.html',
                    {'sensor': sensor} # Truyền đối tượng sensor vào context của partial template
                )
                node_text = f"Sensor: {sensor.name} ({sensor.sensor_id}) - Type: {sensor.sensor_type}"
                jstree_nodes.append({
                    "id": f"{sensor.id}", # Dùng sensor.id (pk) thay vì sensor_id (CharField) để đảm bảo duy nhất
                    "parent": f"{esp.esp_id}", # Parent là ESP
                    "text": rendered_html_text,
                    "type": "sensor"
                })
                
    return jstree_nodes

def get_metric_unit(metric_type):
    """
    Trả về đơn vị hiển thị cho từng loại metric.
    """
    if metric_type == 'CPU':
        return '%'
    elif metric_type == 'RAM':
        return 'GB'
    elif metric_type == 'DISK':
        return 'GB'
    elif metric_type == 'TEMP':
        return '°C'
    return ''

def get_metric_data(pi_id,metric_type):
    
    valid_metric_types = [choice[0] for choice in PiMetricHistory.METRIC_TYPE_CHOICES]
    # Kiểm tra xem metric_type có tồn tại và có hợp lệ không
    if not metric_type or metric_type.upper() not in valid_metric_types:
        return None
        
    pi=RaspberryPi.objects.filter(pk=pi_id).first()
    
    if pi is None:
        return None
    

    history_data = PiMetricHistory.objects.filter(
            raspberry_pi=pi,
            metric_type=metric_type.upper() # Đảm bảo khớp với giá trị đã lưu (chữ hoa)
        ).order_by(
            'timestamp' # Sắp xếp theo thời gian tăng dần cho biểu đồ
        )[:50] # Lấy 50 điểm dữ liệu gần nhất (có thể tùy chỉnh)
        
    
    labels = []       # Dành cho trục X (thời gian)
    data_points = []  # Dành cho trục Y (giá trị metric)
    
    for record in history_data:
        # Chuyển đổi timestamp từ UTC (trong database) sang múi giờ địa phương của server
        local_time = timezone.localtime(record.timestamp)

        # Định dạng thời gian. Ví dụ: "14:30" hoặc "Jul 12 09:30"
        labels.append(local_time.strftime('%H:%M')) 
        
        # Thêm giá trị metric vào mảng data_points
        data_points.append(record.value)
    
    metric_unit = get_metric_unit(metric_type.upper())
    
    return {
                'labels': labels,      # Mảng các nhãn (thời gian)
                'data': data_points,   # Mảng các giá trị metric
                'metric_unit': metric_unit # Đơn vị của metric (ví dụ: %, GB, °C)
            }


def get_get_sensor_readings_grouped_by_type(esp_id,start_dt,end_dt):

    esp=EspDevice.objects.filter(pk=esp_id).first()
    
    if esp is None:
        return None
    
    readings = (
        SensorReading.objects
        .filter(esp_device=esp,timestamp_device__range=(start_dt, end_dt))
        #.select_related('sensor')  # tối ưu
        .order_by('timestamp_device')  # đảm bảo đúng thứ tự thời gian
        .values('sensor__sensor_type', 'timestamp_device', 'value')  # chỉ lấy trường cần
    )
    
    sensor_data = defaultdict(list)
    for r in readings:
        sensor_type = r['sensor__sensor_type']
        sensor_data[sensor_type].append({
            'x': r['timestamp_device'].isoformat(),
            'y': r['value'],
        })
        
    return sensor_data

def parse_search_filter(search_str, field_name="value"):
    """
    Phân tích search_str (ví dụ: '>60 && <70') và trả về Q object phù hợp.
    """
    if not search_str:
        return Q()

    search_str = search_str.strip()
    and_split = search_str.split('&&')
    or_split = search_str.split('||')

    def parse_condition(cond):
        cond = cond.strip()
        if m := re.match(r'(>=|<=|>|<|=)?\s*(-?\d+(\.\d+)?)', cond):
            op, number, _ = m.groups()
            number = float(number)
            if op == '>':
                return Q(**{f"{field_name}__gt": number})
            elif op == '>=':
                return Q(**{f"{field_name}__gte": number})
            elif op == '<':
                return Q(**{f"{field_name}__lt": number})
            elif op == '<=':
                return Q(**{f"{field_name}__lte": number})
            elif op == '=' or op is None:
                return Q(**{f"{field_name}": number})
        return Q()

    if '&&' in search_str:
        return Q() & parse_condition(and_split[0]) & parse_condition(and_split[1])
    elif '||' in search_str:
        return Q() | parse_condition(or_split[0]) | parse_condition(or_split[1])
    else:
        return parse_condition(search_str)


#-----------------------------------------tree--------------------------------------------#

class StartingPageView(View):
    #template_name='tutor_app/index.html'
    def get(self,request):
        
        tree_data =get_tree_data_for_jstree()
        
        context = {
        'tree_nodes_json': tree_data, # Tên biến này sẽ được dùng trong template
        }
        
        return render(request, "iot_app/index.html" ,context)

class SensorUpdateAPIView(View):
    
    def get(self,request):
        
        #print('nhận yêu cầu ajax')
        updated_nodes_data = []

        tree_data =get_tree_data_for_jstree()
        
        for node in tree_data:
        
            updated_nodes_data.append({
                    'id': node["id"],
                    'html': node['text']
                })
        return JsonResponse(updated_nodes_data, safe=False)

#-------------------------------------------Raspi---------------------------------------------#

class RaspberryDetailView(View):
    
    def get(self,request,pi_id): 
        
        print(f'nhan request---:pi_id={pi_id}')
        
        pi = get_object_or_404(RaspberryPi, pi_id=pi_id)
        esp_devices = pi.esp_devices.all().order_by('name')
        pi_status_display = "Online" if pi.is_online() else "Offline"
        
        context = {
            'pi': pi, # Đối tượng RaspberryPi đầy đủ
            'pi_status_display': pi_status_display, # Dùng property để hiển thị trạng thái đã kết hợp
            'esp_devices': esp_devices, # QuerySet của các EspDevice liên quan
        }
        html_content = render_to_string('iot_app/raspi_node_detail.html', context,request=request)
        return JsonResponse({'html': html_content})

class RaspberryInfoAndMonitorPartialView(View):
    
    def get(self, request, pi_id):    
        pi = get_object_or_404(RaspberryPi, pi_id=pi_id)
        esp_devices = pi.esp_devices.all().order_by('name')
        pi_status_display = "Online" if pi.is_online() else "Offline"
        
        context = {
            'pi': pi, # Đối tượng RaspberryPi đầy đủ
            'pi_status_display': pi_status_display, # Dùng property để hiển thị trạng thái đã kết hợp
            'esp_devices': esp_devices, # QuerySet của các EspDevice liên quan
        }

        html_info = render_to_string('iot_app/partials/pi_view/raspi_info_partial.html', context, request=request)
        html_monitor = render_to_string('iot_app/partials/pi_view/raspi_status_partial.html', context, request=request)

        return JsonResponse({
            'info_html': html_info,
            'monitor_html': html_monitor,
        })

class RaspberryChartsView(View):
    def get(self,request,pi_id):
        result = {}
        print(pi_id)
        for metric in ['CPU', 'RAM', 'TEMP']:
            
            data = get_metric_data(pi_id, metric)  # Hàm bạn đã có sẵn
            
            if data is not None:
                result[metric] = {
                    'labels': data['labels'],
                    'data': data['data'],
                    'unit': data.get('metric_unit', '')
                }
            else:
                result[metric]=None

        return JsonResponse(result)

@method_decorator(csrf_exempt, name='dispatch') # <-- Rất quan trọng cho API từ thiết bị
class RaspberryDataIngestionView(View):
    """
    API Endpoint để nhận dữ liệu metrics từ Raspberry Pi.
    Pi sẽ gửi dữ liệu định kỳ tới endpoint này thông qua phương thức POST.
    """
    def post(self, request, pi_id): # <-- Sử dụng phương thức POST và nhận pi_id từ URL
        try:
            pi = get_object_or_404(RaspberryPi, pi_id=pi_id)
            # 2. Phân tích dữ liệu nhận được từ body của request (dạng JSON)
            # request.body chứa dữ liệu thô từ HTTP request
            data = json.loads(request.body)

            # 3. Lấy các giá trị metrics từ dữ liệu đã phân tích
            # Sử dụng .get(key, default_value) để tránh KeyError nếu trường không có
            # và sử dụng float() để đảm bảo kiểu dữ liệu đúng
            cpu_usage = float(data.get('cpu_usage', pi.cpu_usage))
            ram_usage_gb = float(data.get('ram_usage_gb', pi.ram_usage_gb))
            disk_space_gb = float(data.get('disk_space_gb', pi.disk_space_gb))
            cpu_temperature_celsius = float(data.get('cpu_temperature_celsius', pi.cpu_temperature_celsius))
            
            # 4. Xử lý Timestamp của dữ liệu đến
            # Thiết bị có thể gửi timestamp của riêng nó
            timestamp_from_device_str = data.get('timestamp')
            
            if timestamp_from_device_str:
                try:
                    # Chuyển đổi timestamp string từ thiết bị sang datetime object
                    # Nếu timestamp có múi giờ (e.g., '2025-07-12T14:30:00+07:00')
                    # fromisoformat sẽ tự động tạo aware datetime
                    timestamp_to_save = datetime.fromisoformat(timestamp_from_device_str)
                    
                    # Đảm bảo nó là aware datetime. Nếu nó là naive (e.g. '2025-07-12T14:30:00')
                    # và bạn biết múi giờ của thiết bị, bạn cần localize nó:
                    # from datetime import datetime
                    # import pytz
                    # device_naive_datetime = datetime.strptime(timestamp_from_device_str, "%Y-%m-%dT%H:%M:%S") # Hoặc định dạng khác
                    # local_tz = pytz.timezone('Asia/Ho_Chi_Minh') # Múi giờ của thiết bị
                    # timestamp_to_save = local_tz.localize(device_naive_datetime)

                except ValueError:
                    # Nếu định dạng timestamp không đúng, sử dụng giờ server
                    timestamp_to_save = timezone.now()
            else:
                # Nếu Pi không gửi timestamp, sử dụng giờ hiện tại của server (aware)
                timestamp_to_save = timezone.now()

            # 5. Cập nhật các trường dữ liệu HIỆN TẠI của RaspberryPi
            pi.cpu_usage = cpu_usage
            pi.ram_usage_gb = ram_usage_gb
            pi.disk_space_gb = disk_space_gb
            pi.cpu_temperature_celsius = cpu_temperature_celsius
            pi.last_seen = timestamp_to_save # Cập nhật thời gian cuối cùng thấy
            # Các trường khác có thể cập nhật: pi.local_ip_address = data.get('ip_address', pi.local_ip_address)
            pi.save() # <-- Lưu thay đổi vào database cho RaspberryPi

            # 6. Tạo các bản ghi LỊCH SỬ vào PiMetricHistory cho TỪNG METRIC
            # Ghi lại lịch sử CPU Usage
            PiMetricHistory.objects.create(
                raspberry_pi=pi,
                metric_type='CPU', # Sử dụng giá trị từ METRIC_TYPE_CHOICES
                value=cpu_usage,
                timestamp=timestamp_to_save
            )
            # Ghi lại lịch sử RAM Usage
            PiMetricHistory.objects.create(
                raspberry_pi=pi,
                metric_type='RAM',
                value=ram_usage_gb,
                timestamp=timestamp_to_save
            )
            # Ghi lại lịch sử Disk Space
            PiMetricHistory.objects.create(
                raspberry_pi=pi,
                metric_type='DISK',
                value=disk_space_gb,
                timestamp=timestamp_to_save
            )
            # Ghi lại lịch sử CPU Temperature
            PiMetricHistory.objects.create(
                raspberry_pi=pi,
                metric_type='TEMP',
                value=cpu_temperature_celsius,
                timestamp=timestamp_to_save
            )
            
            # (Tùy chọn) Logic cập nhật has_active_alarms dựa trên ngưỡng
            # Bạn có thể kiểm tra ngưỡng ở đây và cập nhật pi.has_active_alarms = True/False

            # 7. Trả về phản hồi thành công
            return JsonResponse({'status': 'success', 'message': 'Metrics updated and history recorded successfully'})

        except RaspberryPi.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Raspberry Pi with this ID not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body'}, status=400)
        except Exception as e:
            # Bắt các lỗi chung để trả về phản hồi lỗi server 500
            print(f"Error processing Raspberry Pi data: {e}")
            return JsonResponse({'status': 'error', 'message': f'Internal server error: {str(e)}'}, status=500)

#----------------------------------------------Esp---------------------------------------------#

class EspDetailView(View):
    
    def get(self,request,esp_id): 
        
        print(f'nhan request---:pi_id={esp_id}')
        esp = get_object_or_404(EspDevice, esp_id=esp_id)
        
        # sensors =  esp.sensors   -> cho ra danh sách sensor
        # sensors=   esp.sensors.prefetch_related(Prefetch(forgein_key, querryset='...', to_atrr='latest_readings_all'))  vẫn cho ra danh sách sensor , nhưng mỗi sensor lại thêm thuộc tính latest_readings_all là kết quả truy vấn querreset thông qua khóa ngoại  (vì mỗi sensor lại gắn nhiều bản ghi thông qua khóa ngoại readings) như vậy  to_atrr sẽ là danh sách các record SensorReading
        
        pi_timezone_str = esp.raspberry_pi.timezone or 'UTC'
        
        sensors = esp.sensors.prefetch_related(
            Prefetch(
                'readings',
                queryset=SensorReading.objects.order_by('-timestamp_device'),
                to_attr='latest_readings_all'
            )
        )
        
        for sensor in sensors: 
            sensor.latest_readings = sensor.latest_readings_all[:5]
                           
        context = {
            'esp': esp, # Đối tượng RaspberryPi đầy đủ
            'timezone':pi_timezone_str,
            'sensors': sensors, # Dùng property để hiển thị trạng thái đã kết
        }      
        
        html_content = render_to_string('iot_app/esp_node_detail.html',context)
        return JsonResponse({'html': html_content})

class EspChartsView(View):
    
    def get(self,request,esp_id):
        
        date_start = request.GET.get('start')
        date_end = request.GET.get('end')
        
        start_dt = parse_datetime(date_start)
        
        end_dt = parse_datetime(date_end)
        
        if not start_dt or not end_dt:
            return JsonResponse({'error': 'Tham số thời gian không hợp lệ.'}, status=400)
                
        data = get_get_sensor_readings_grouped_by_type(esp_id,start_dt,end_dt)
        
        if data is None:
            return JsonResponse({'error': 'ESP not found'}, status=404)
        print(data)
        return JsonResponse(data)

class EspSensorsView(View):
     
    def get(self,request,esp_id):
        
        print(f'nhan request---:pi_id={esp_id}')
        esp = get_object_or_404(EspDevice, esp_id=esp_id)
        
        # sensors =  esp.sensors   -> cho ra danh sách sensor
        # sensors=   esp.sensors.prefetch_related(Prefetch(forgein_key, querryset='...', to_atrr='latest_readings_all'))  vẫn cho ra danh sách sensor , nhưng mỗi sensor lại thêm thuộc tính latest_readings_all là kết quả truy vấn querreset thông qua khóa ngoại  (vì mỗi sensor lại gắn nhiều bản ghi thông qua khóa ngoại readings) như vậy  to_atrr sẽ là danh sách các record SensorReading
        
        pi_timezone_str = esp.raspberry_pi.timezone or 'UTC'
        
        sensors = esp.sensors.prefetch_related(
            Prefetch(
                'readings',
                queryset=SensorReading.objects.order_by('-timestamp_device'),
                to_attr='latest_readings_all'
            )
        )
        
        for sensor in sensors: 
            sensor.latest_readings = sensor.latest_readings_all[:5]
                           
        context = {
            'esp': esp, # Đối tượng RaspberryPi đầy đủ
            'timezone':pi_timezone_str,
            'sensors': sensors, # Dùng property để hiển thị trạng thái đã kết
        }      
        
        html_content = render_to_string('iot_app/partials/esp_tabs/esp_tabs_sensor.html',context)
        return JsonResponse({'html': html_content})


#----------------------------------------------sensor-------------------------------------------#
class SensorDetailView(View):
    
    def get(self,request,sensor_id):
        
        form = None
        
        sensor = get_object_or_404(Sensor.objects.select_related('esp_device__raspberry_pi'), pk=sensor_id)
        
        timezone = sensor.esp_device.raspberry_pi.timezone
        # Lấy bản ghi SensorReading mới nhất
        latest_reading = sensor.readings.order_by('-timestamp_device').first()
               
        if sensor.sensor_type=='temperature':
            
            print('tạo model form:  SensorTemperatureConfigForm')
            
            try:
                config_instance = sensor.temperature_config
                print(config_instance)
            except:
                config_instance = None
                print('config_instance: None')
        
            form = SensorTemperatureConfigForm(instance=config_instance,sensor_instance=sensor)
            
        elif  sensor.sensor_type=='sound':
            
            print('tạo model form:  SensorSoundConfigForm')
            
            try:
                config_instance = sensor.sound_config
                print(config_instance)
            except:
                config_instance = None
                print('config_instance: None')
        
            form = SensorSoundConfigForm(instance=config_instance,sensor_instance=sensor)
            
        elif sensor.sensor_type=='vibration':
            
            print('tạo model form:  SensorVibrationConfigForm')
            
            try:
                config_instance = sensor.vibration_config
                print(config_instance)
            except:
                config_instance = None
                print('config_instance: None')
        
            form = SensorVibrationConfigForm(instance=config_instance,sensor_instance=sensor)
            
        context = {
            'sensor':sensor,
            'timezone':timezone,
            'latest_reading':latest_reading,
            'form':form
        }
        html_content=render_to_string('iot_app/sensor_node_detail.html', context,request=request)
        return JsonResponse({'html':html_content})
    
class SensorChartView(View):
    
    def get(self,request,sensor_id):
        
        print('nhan yeu cau lay bieu do')
        
        date_start = request.GET.get('start')
        date_end = request.GET.get('end')
        
        start_dt = parse_datetime(date_start)
        end_dt = parse_datetime(date_end)
        
        print(f'Thoi gian bat dau: {date_start}  convert to  {start_dt}')
        print(f'Thoi gian ket thuc: {date_end}  convert to  {end_dt}')
        
        
        if not start_dt or not end_dt:
            return JsonResponse({'error': 'Tham số thời gian không hợp lệ.'}, status=400)
        
        sensor=Sensor.objects.filter(pk=sensor_id).first()
        
        if sensor is None:
            return JsonResponse({'error': 'Sensor không tồn tại'}, status=400)
        
        readings=sensor.readings.filter(
            timestamp_device__range=(start_dt, end_dt)
        ).order_by('timestamp_device').values('timestamp_device', 'value')
        
        data = defaultdict(list)
        
        sensor_type=sensor.sensor_type
        
        for r in readings:
            data[sensor_type].append({
                'x': r['timestamp_device'].isoformat(),
                'y': r['value'],
            })

        return JsonResponse(data,safe=False)

class SensorTableView(View):
    
    def get(self,request,sensor_id):
        
        print('nhan yeu cau lay du lieu cho table')
        
        event=request.GET.get('event')
        
        draw = int(request.GET.get('draw'))  
        start = int(request.GET.get('start'))  
        length = int(request.GET.get('length'))  
        print(f'draw={draw} - start: {start} - length: {length}')
        
        order_column_index = request.GET.get('order[0][column]')
        order_dir = request.GET.get('order[0][dir]')
        order_column_name = request.GET.get(f'columns[{order_column_index}][data]')            
        search_value = request.GET.get('search[value]', '').strip()
        
        order_parameter=None
        if order_column_index is not None:
             order_parameter=order_column_name
             if order_dir == 'desc':
                    order_parameter = '-' + order_parameter
        
        print(f'order_column_index={order_column_index} - order_dir={order_dir} -  order_column_name ={order_column_name}' )
        
        column_default=request.GET.get('column_default')
        
        print(f'column_default={column_default}')
        
        print(event)
        
        if event=='init':
            
            print('su kien load page')
            
            sensor=Sensor.objects.filter(pk=sensor_id).first()
            if sensor is None:
                return JsonResponse({'error': 'Sensor không tồn tại'}, status=400)
            
            sensor_type=sensor.sensor_type
            
            if order_parameter:
                try:
                    readings_queryset =sensor.readings.order_by(order_parameter)
                except Exception as err:
    
                    readings_queryset =sensor.readings.order_by(column_default)
            else:
                readings_queryset =sensor.readings.order_by(column_default)
                
        
            total_records = readings_queryset.count()
            
            if search_value:
                print(f'search:{search_value}')
                
                q_object = parse_search_filter(search_value)                
                readings_queryset = readings_queryset.filter(q_object)                              
            
            print('---')
            
            filtered_count = readings_queryset.count()
            paginated_readings = readings_queryset[start:start+length]
            
            data = []
            for i, r in enumerate(paginated_readings, start=start + 1):
                data.append({
                    "index": i,
                    "timestamp_device": r.timestamp_device,
                    "value": r.value,
                    "timestamp_server": r.timestamp_server,
                    "sensor_type": sensor_type,
                })
        
            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": filtered_count,
                "data": data
            },safe=False )
            
        elif event=='filter':
            
            print('su kien filter')
            
            start_date_ = request.GET.get('start_date')
            stop_date_= request.GET.get('stop_date')
            
            start_date = parse_datetime(start_date_)
            stop_date = parse_datetime(stop_date_)
            
            print(f'start_date:{start_date} - stop_date:{stop_date}')
            
            sensor=Sensor.objects.filter(pk=sensor_id).first()
            if sensor is None:
                return JsonResponse({'error': 'Sensor không tồn tại'}, status=400)
            
            sensor_type=sensor.sensor_type
            
            if order_parameter:
                try:
                    readings_queryset =sensor.readings.order_by(order_parameter)
                except:
                    readings_queryset =sensor.readings.order_by(column_default)
            else:
                readings_queryset =sensor.readings.order_by(column_default)
            print('-----')
            total_records = readings_queryset.count()
            
            paginated_readings = readings_queryset[start:start+length]
            
            
            readings_queryset_2 = readings_queryset.filter(
                    timestamp_device__range=(start_date, stop_date)
                )
            
            
            if search_value:
                q_object = parse_search_filter(search_value, field_name="value")
                readings_queryset_2 = readings_queryset_2.filter(q_object)

            
            filtered_count = readings_queryset_2.count()
            
            paginated_readings = readings_queryset_2[start:start + length]
            
            
            data = []
            for i, r in enumerate(paginated_readings, start=start + 1):
                data.append({
                    "index": i,
                    "timestamp_device": r.timestamp_device,
                    "value": r.value,
                    "timestamp_server": r.timestamp_server,
                    "sensor_type": sensor_type,
                })
        
        
            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": filtered_count,
                "data": data
            },safe=False )
            
            
        data = {'data': []}
        return JsonResponse(data,safe=False)

#-----------Giao diện cài đật cho từng cảm biến------------#

class SensorTemperatureConfigView(View):
    
    def post(self,request):
        
        sensor_id = request.POST.get("sensor_id")
        sensor = Sensor.objects.get(pk=sensor_id)
        config_instance = sensor.temperature_config  
        
        print(sensor_id)
        
        form  =SensorTemperatureConfigForm(
            request.POST,
            instance=config_instance,
            sensor_instance=sensor
        )
        
        if form.is_valid():
            form.save()
            print('form hợp lệ - lưu thành công')
            # # Render lại form (có thể đã cập nhật giá trị)
            rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_temperature.html",{
                "form": form,
                "sensor": sensor,
                "error": False
            }, request=request)
            
            return JsonResponse({"html": rendered_form})
        
        print("form không hợp lệ")
        
        rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_temperature.html", {
                "form": form,
                "sensor": sensor,
                "error":True
            }, request=request)
            
        return JsonResponse({"html": rendered_form})

class SensorSoundConfigView(View):
    
    def post(self,request):
        
        sensor_id = request.POST.get("sensor_id")
        sensor = Sensor.objects.get(pk=sensor_id)
        config_instance = sensor.sound_config  
        
        print(sensor_id)
        
        form  =SensorSoundConfigForm(
            request.POST,
            instance=config_instance,
            sensor_instance=sensor
        )
        
        if form.is_valid():
            form.save()
            print('form hợp lệ - lưu thành công')
            # # Render lại form (có thể đã cập nhật giá trị)
            rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_sound.html",{
                "form": form,
                "sensor": sensor,
                "error": False
            }, request=request)
            
            return JsonResponse({"html": rendered_form})
        
        print("form không hợp lệ")
        
        rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_sound.html", {
                "form": form,
                "sensor": sensor,
                "error":True
            }, request=request)
            
        return JsonResponse({"html": rendered_form})
    
class SensorVibrationConfigView(View):
        
    def post(self,request):
        
        sensor_id = request.POST.get("sensor_id")
        sensor = Sensor.objects.get(pk=sensor_id)
        config_instance = sensor.vibration_config  
        
        print(sensor_id)
        
        form  =SensorVibrationConfigForm(
            request.POST,
            instance=config_instance,
            sensor_instance=sensor
        )
        
        if form.is_valid():
            #form.save()
            print('form hợp lệ - lưu thành công')
            # # Render lại form (có thể đã cập nhật giá trị)
            rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_vibration.html",{
                "form": form,
                "sensor": sensor,
                "error": False
            }, request=request)
            
            return JsonResponse({"html": rendered_form})
        
        print("form không hợp lệ")
        
        rendered_form = render_to_string("iot_app/partials/sensor_tabs/sensor_setting_vibration.html", {
                "form": form,
                "sensor": sensor,
                "error":True
            }, request=request)
            
        return JsonResponse({"html": rendered_form})
    
#-------------------------------------------api dieu khien--------------------------------------#

#----------------test----------------------------------------------------------------------------

class PiMetricHistoryView(View):
    
    def get(self,request,pi_id):  
    
        try:
            
            pi=get_object_or_404(RaspberryPi, pi_id=pi_id)
            metric_type = request.GET.get('type')
            valid_metric_types = [choice[0] for choice in PiMetricHistory.METRIC_TYPE_CHOICES]
            # Kiểm tra xem metric_type có tồn tại và có hợp lệ không
            if not metric_type or metric_type.upper() not in valid_metric_types:
                return JsonResponse(
                    {'error': 'Invalid or missing "type" parameter. Valid types are: ' + ', '.join(valid_metric_types)}, 
                    status=400 # Trả về lỗi Bad Request nếu tham số không hợp lệ
                )
            
            history_data = PiMetricHistory.objects.filter(
                    raspberry_pi=pi,
                    metric_type=metric_type.upper() # Đảm bảo khớp với giá trị đã lưu (chữ hoa)
                ).order_by(
                    'timestamp' # Sắp xếp theo thời gian tăng dần cho biểu đồ
                )[:50] # Lấy 50 điểm dữ liệu gần nhất (có thể tùy chỉnh)
                
            
            labels = []       # Dành cho trục X (thời gian)
            data_points = []  # Dành cho trục Y (giá trị metric)
            
            for record in history_data:
                # Chuyển đổi timestamp từ UTC (trong database) sang múi giờ địa phương của server
                local_time = timezone.localtime(record.timestamp)
        
                # Định dạng thời gian. Ví dụ: "14:30" hoặc "Jul 12 09:30"
                labels.append(local_time.strftime('%H:%M')) 
                
                # Thêm giá trị metric vào mảng data_points
                data_points.append(record.value)
            
            metric_unit = self._get_metric_unit(metric_type.upper())
            
            return JsonResponse({
                'labels': labels,      # Mảng các nhãn (thời gian)
                'data': data_points,   # Mảng các giá trị metric
                'metric_unit': metric_unit # Đơn vị của metric (ví dụ: %, GB, °C)
            })
                
        except RaspberryPi.DoesNotExist:
            return JsonResponse({'error': 'Raspberry Pi not found'}, status=404)
            
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)
            
            
            
    def _get_metric_unit(self, metric_type):
        """
        Trả về đơn vị hiển thị cho từng loại metric.
        """
        if metric_type == 'CPU':
            return '%'
        elif metric_type == 'RAM':
            return 'GB'
        elif metric_type == 'DISK':
            return 'GB'
        elif metric_type == 'TEMP':
            return '°C'
        return ''

def test_js_tree(request):
    
    tree_data = [
        { "id": "node_1", "parent": "#", "text": "Root Node 1 (from Context)" },
        { "id": "node_2", "parent": "#", "text": "Root Node 2 (from Context)" },
        { "id": "node_1_1", "parent": "node_1", "text": "Child of Root 1 (Context)" },
        { "id": "node_1_2", "parent": "node_1", "text": "Another Child of Root 1 (Context)" },
        { "id": "node_2_1", "parent": "node_2", "text": "Child of Root 2 (Context)" },
        { "id": "node_1_1_1", "parent": "node_1_1", "text": "Grandchild of Root 1 (Context)" }
    ]
    context = {
        'tree_nodes_json': tree_data, # Tên biến này sẽ được dùng trong template
    }
    return render(request,'iot_app/simple_js_tree.html',context)