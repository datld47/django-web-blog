from django.contrib import admin
import nested_admin
import nested_admin.nested 
from .models import RaspberryPi,EspDevice,Sensor,SensorReading,PiMetricHistory,SensorTemperatureConfig,SensorSoundConfig,SensorVibrationConfig

# class ImageExerciseInline(nested_admin.nested.NestedTabularInline):
#     model=Image_Exercise
#     extra=0

# class ExerciseInline(nested_admin.nested.NestedTabularInline):
#     model=Exercise
#     extra=0
#     #inlines=[ImageExerciseInline]

# class LessionInline(nested_admin.nested.NestedStackedInline):
#     model=Lession
#     extra=0
#     #inlines=[ExerciseInline]

# class ResultExerciseInline(nested_admin.nested.NestedStackedInline):
#     model=ResultExercise
#     extra=0

# class CourseAdimn(nested_admin.nested.NestedModelAdmin):
#     inlines=[LessionInline]
    
# class ExerciseAdmin(nested_admin.nested.NestedModelAdmin):
#     inlines=[ImageExerciseInline]

# # class StudentAdmin(nested_admin.nested.NestedModelAdmin):
# #     inlines=[ResultExerciseInline]
 
admin.site.register(RaspberryPi)
admin.site.register(EspDevice)
admin.site.register(Sensor)
admin.site.register(SensorReading)
admin.site.register(PiMetricHistory)
admin.site.register(SensorTemperatureConfig)
admin.site.register(SensorSoundConfig)
admin.site.register(SensorVibrationConfig)