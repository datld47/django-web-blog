from django.urls import path
from . import views


urlpatterns = [
    
    path("",views.StartingPageView.as_view(),name="starting-page"),
    path("api/sensor-updates/",views.SensorUpdateAPIView.as_view(),name='sensor-update-page'),
    path('api/raspberry_pi/<str:pi_id>/',views.RaspberryDetailView.as_view(),name='raspi-detail-page'),
    #path('api/raspberry_pi/metric_history/<str:pi_id>/',views.PiMetricHistoryView.as_view(),name='raspi-metric-history-page'),
    path('api/raspberry_pi/info_and_monitor_partial/<str:pi_id>/',views.RaspberryInfoAndMonitorPartialView.as_view(),name='raspi-info-monitor-page'),
    path('api/raspberry_pi/metric_history_bundle/<str:pi_id>/',views.RaspberryChartsView.as_view(),name='raspi-history-page'),
    path('api/raspberry_pi/post_data/<str:pi_id>/', views.RaspberryDataIngestionView.as_view(), name='raspi-post-data'),
    
    path('api/esp_device/<str:esp_id>/',views.EspDetailView.as_view(),name='esp-detail-page'),
    path('api/esp/charts/<str:esp_id>/',views.EspChartsView.as_view(),name='esp-charts-page'),
    path('api/esp/sensors/<str:esp_id>/',views.EspSensorsView.as_view(),name='esp-sensors-page'),
    
    path('api/sensor/<str:sensor_id>/',views.SensorDetailView.as_view(),name='sensor-detail-page'),
    path('api/sensor/charts/<str:sensor_id>/',views.SensorChartView.as_view(),name='sensor-charts-page'),
    path('api/sensor/table/<str:sensor_id>/',views.SensorTableView.as_view(),name='sensor-table-page'),
    
    path('sensor/temperature/config/',views.SensorTemperatureConfigView.as_view(),name='sensor_temperature_config_page'),
    path('sensor/sound/config/',views.SensorSoundConfigView.as_view(),name='sensor_sound_config_page'),
    path('sensor/vibration/config/',views.SensorVibrationConfigView.as_view(),name='sensor_vibration_config_page'),  
    
    
    # path('api/esp/<str:pi_id>',views.EspDetailView.as_view(),name='esp-detail-page'),
    #path("test/tree",views.test_js_tree,name="test-page-tree"),
    # path("login",views.LoginFormView.as_view(),name="login-page"),
    # path("register",views.RegiserFormView.as_view() , name="register-page"),
    # path("hello",views.HelloView.as_view() , name="hello-page")
    # # path("posts/<slug:slug>",views.SinglePostView.as_view(),name="post-detail-page"),   #/posts/my-first-post
    # # path("read-later",views.ReadLaterView.as_view(),name='read-later')
]
