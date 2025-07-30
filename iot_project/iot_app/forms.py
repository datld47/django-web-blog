from django import forms
from django.db import transaction
from .models import Sensor, SensorTemperatureConfig,SensorSoundConfig,SensorVibrationConfig

class SensorTemperatureConfigForm(forms.ModelForm):
    sensor_name = forms.CharField(label="Tên cảm biến", required=True)
    class Meta:
        model = SensorTemperatureConfig
        fields = ['read_interval_seconds', 'threshold_low', 'threshold_high']

    def __init__(self, *args, **kwargs):
        self.sensor_instance = kwargs.pop('sensor_instance', None)
        super().__init__(*args, **kwargs)
        if self.sensor_instance:
            self.fields['sensor_name'].initial = self.sensor_instance.name
        
        self.fields['read_interval_seconds'].label = "Chu kỳ đọc dữ liệu (giây)"
        self.fields['threshold_low'].label = "Ngưỡng cảnh báo thấp (°C)"
        self.fields['threshold_high'].label = "Ngưỡng cảnh báo cao (°C)"
        self.fields['sensor_name'].label = "Tên cảm biến"
        
        self.order_fields([
                'sensor_name',
                'read_interval_seconds',
                'threshold_low',
                'threshold_high',
            ])

    @transaction.atomic
    def save(self, commit=True):
        config = super().save(commit=False)
        if self.sensor_instance:
            self.sensor_instance.name = self.cleaned_data['sensor_name']  #nạp field  vào  sensor_instance
            self.sensor_instance.save() #lưu xuống database
            config.sensor = self.sensor_instance  #nạp lại dữ liệu liên kết 
        if commit:
            config.save()
        return config

class SensorSoundConfigForm(forms.ModelForm):
    sensor_name = forms.CharField(label="Tên cảm biến", required=True)
    class Meta:
        model = SensorSoundConfig
        fields = ['gain_multiplier', 'sampling_interval_ms', 'sound_threshold_mv','hold_time_ms','read_interval_seconds','operating_mode']

    def __init__(self, *args, **kwargs):
        self.sensor_instance = kwargs.pop('sensor_instance', None)
        super().__init__(*args, **kwargs)
        if self.sensor_instance:
            self.fields['sensor_name'].initial = self.sensor_instance.name
        
        self.fields['gain_multiplier'].label = "Hệ số khuyếch đại"
        self.fields['sampling_interval_ms'].label = "Chu kỳ lấy mẫu (ms)"
        self.fields['sound_threshold_mv'].label = "Ngưỡng cảnh báo âm thanh (mv)"
        self.fields['hold_time_ms'].label = "Thời gian tối thiểu âm thanh vượt ngưỡng (ms)"
        self.fields['read_interval_seconds'].label = "Chu kỳ đọc dữ liệu (giây)"
        self.fields['sensor_name'].label = "Tên cảm biến"
        self.fields['operating_mode'].label = "Chế độ hoạt động"
        
        self.order_fields([
                'sensor_name',
                'read_interval_seconds',
                'operating_mode',
                'gain_multiplier',
                'sampling_interval_ms',
                'sound_threshold_mv',
                'hold_time_ms'
            ])

    @transaction.atomic
    def save(self, commit=True):
        config = super().save(commit=False)
        if self.sensor_instance:
            self.sensor_instance.name = self.cleaned_data['sensor_name']  #nạp field  vào  sensor_instance
            self.sensor_instance.save() #lưu xuống database
            config.sensor = self.sensor_instance  #nạp lại dữ liệu liên kết 
        if commit:
            config.save()
        return config

class SensorVibrationConfigForm(forms.ModelForm):
    sensor_name = forms.CharField(label="Tên cảm biến", required=True)
    class Meta:
        model = SensorVibrationConfig
        fields = ['vibration_threshold_mv', 'debounce_time_ms', 'sampling_interval_ms','read_interval_seconds','operating_mode']

    def __init__(self, *args, **kwargs):
        self.sensor_instance = kwargs.pop('sensor_instance', None)
        super().__init__(*args, **kwargs)
        if self.sensor_instance:
            self.fields['sensor_name'].initial = self.sensor_instance.name
        
        self.fields['vibration_threshold_mv'].label = "Ngưỡng cánh báo rung (mv)"
        self.fields['debounce_time_ms'].label = "thời gian chống dội"
        self.fields['sampling_interval_ms'].label = "Chu kỳ lấy mẫu với cảm biến analog"
        self.fields['read_interval_seconds'].label = "Chu kỳ đọc dữ liệu (giây)"
        self.fields['sensor_name'].label = "Tên cảm biến"
        self.fields['operating_mode'].label = "Chế độ hoạt động"
        
        self.order_fields([
                'sensor_name',
                'read_interval_seconds',
                'operating_mode',
                'debounce_time_ms',
                'vibration_threshold_mv',
                'sampling_interval_ms',
                'sound_threshold_mv',
            ])

    @transaction.atomic
    def save(self, commit=True):
        config = super().save(commit=False)
        if self.sensor_instance:
            self.sensor_instance.name = self.cleaned_data['sensor_name']  #nạp field  vào  sensor_instance
            self.sensor_instance.save() #lưu xuống database
            config.sensor = self.sensor_instance  #nạp lại dữ liệu liên kết 
        if commit:
            config.save()
        return config
    
    
    
