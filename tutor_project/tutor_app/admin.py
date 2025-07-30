from django.contrib import admin
import nested_admin
import nested_admin.nested 
from .models import Image_Exercise,Exercise,Student,Account_Student,LogFile_Student,Lession,Course,ResultExercise

# Register your models here.
# class PostAdmin(admin.ModelAdmin):
#     list_filter = ("author", "tags", "date",)
#     list_display = ("title", "date", "author",)
#     prepopulated_fields = {"slug": ("title",)}

# class CommentAdmin(admin.ModelAdmin):
#     list_display=("user_name","post")


class ImageExerciseInline(nested_admin.nested.NestedTabularInline):
    model=Image_Exercise
    extra=0

class ExerciseInline(nested_admin.nested.NestedTabularInline):
    model=Exercise
    extra=0
    #inlines=[ImageExerciseInline]

class LessionInline(nested_admin.nested.NestedStackedInline):
    model=Lession
    extra=0
    #inlines=[ExerciseInline]

class ResultExerciseInline(nested_admin.nested.NestedStackedInline):
    model=ResultExercise
    extra=0

class CourseAdimn(nested_admin.nested.NestedModelAdmin):
    inlines=[LessionInline]
    
class ExerciseAdmin(nested_admin.nested.NestedModelAdmin):
    inlines=[ImageExerciseInline]

# class StudentAdmin(nested_admin.nested.NestedModelAdmin):
#     inlines=[ResultExerciseInline]
 
admin.site.register(Course,CourseAdimn)
admin.site.register(Lession)
admin.site.register(Image_Exercise)
admin.site.register(Exercise,ExerciseAdmin)
admin.site.register(Student)
admin.site.register(Account_Student)
admin.site.register(LogFile_Student)
admin.site.register(ResultExercise)