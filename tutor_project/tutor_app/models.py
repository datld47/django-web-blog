from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,MinLengthValidator
from django.urls import reverse
from django.utils.text import slugify


# # Create your models here.
# class Tag(models.Model):
#     caption = models.CharField(max_length=20)

#     def __str__(self):
#       return self.caption

# class Author(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email_address = models.EmailField()

#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def __str__(self):
#         return self.full_name()


# class Post(models.Model):
#     title = models.CharField(max_length=150)
#     excerpt = models.CharField(max_length=200)
#     image = models.ImageField(upload_to="posts", null=True)
#     date = models.DateField(auto_now=True)
#     slug = models.SlugField(unique=True, db_index=True)
#     content = models.TextField(validators=[MinLengthValidator(10)])
#     author = models.ForeignKey(
#         Author, on_delete=models.SET_NULL, null=True, related_name="posts")
#     tags = models.ManyToManyField(Tag)
    
#     def __str__(self):
#         return self.title
    
# class Comment(models.Model):
#     user_name=models.CharField(max_length=120,null=False,blank=False)
#     user_email=models.EmailField()
#     text=models.TextField(max_length=400,null=False,blank=False)
#     post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')


class Course(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False)
    
    description = models.CharField(max_length=1000, null=False, blank=False) # Mô tả khóa học chi tiết hơn
    
    # Quy tắc hệ thống để cung cấp cho AI (ví dụ: "Bạn là gia sư toán học lớp 10.")
    system_rule = models.TextField(
        help_text="Quy tắc hệ thống hoặc hướng dẫn cho AI khi tương tác trong khóa học này."
    )
    
    slug = models.SlugField(unique=True, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Lession(models.Model):
    
    title=models.CharField(max_length=500)
    description=models.TextField(max_length=500)
    
    course = models.ForeignKey(
        'Course', # 'Lession' hoặc Lession nếu Lession được định nghĩa trước
        on_delete=models.CASCADE, # Nếu buổi học bị xóa, bài tập liên quan cũng bị xóa
        related_name='lessions', # Cho phép truy cập: lesson_instance.exercises.all()
        help_text="Buổi học mà bài tập này thuộc về.",
        null=True
    )
    
    slug = models.SlugField(unique=True, db_index=True, blank=True) # Thêm blank=True nếu bạn không muốn nhập thủ công
    
    def save(self, *args, **kwargs):
        if not self.slug: # Chỉ tạo slug nếu nó chưa được đặt (ví dụ: khi tạo mới)
            self.slug = slugify(self.title)
        super().save(*args, **kwargs) # Gọi phương thức save gốc để lưu đối tượng
    
    def __str__(self):
        return self.title

class Image_Exercise(models.Model):
    
    title = models.CharField(
        max_length=255,
        help_text="Tên hoặc mô tả ngắn gọn về hình ảnh."
    )
    
    image = models.ImageField(
        upload_to="tutor_app", # Thư mục con trong MEDIA_ROOT để lưu ảnh bài tập
    )
    
    description=models.TextField(
        max_length=500,
        help_text="Mô tả hình cho AI hiểu"
    )
    
    exercise = models.ForeignKey(
        'Exercise', # 'Exercise' hoặc Exercise nếu Exercise được định nghĩa trước
        on_delete=models.CASCADE, # Nếu bài tập bị xóa, hình ảnh liên quan cũng bị xóa
        related_name='images',    # Cho phép truy cập: exercise_instance.images.all()
        help_text="Bài tập mà hình ảnh này thuộc về."
    )
    
    slug = models.SlugField(unique=True, db_index=True, blank=True) # Thêm blank=True nếu bạn không muốn nhập thủ công
    def save(self, *args, **kwargs):
        if not self.slug: # Chỉ tạo slug nếu nó chưa được đặt (ví dụ: khi tạo mới)
            self.slug = slugify(self.title)
        super().save(*args, **kwargs) # Gọi phương thức save gốc để lưu đối tượng
        
    def __str__(self):
        return self.title

class Exercise(models.Model):
    
    title=models.CharField(max_length=500)
    
    description=models.TextField(max_length=500)
    
    guidance=models.TextField(max_length=500)
    
    lesson = models.ForeignKey(
        'Lession', # 'Lession' hoặc Lession nếu Lession được định nghĩa trước
        on_delete=models.CASCADE, # Nếu buổi học bị xóa, bài tập liên quan cũng bị xóa
        related_name='exercises', # Cho phép truy cập: lesson_instance.exercises.all()
        help_text="Buổi học mà bài tập này thuộc về.",
        null=True
    )

    slug = models.SlugField(unique=True, db_index=True, blank=True) # Thêm blank=True nếu bạn không muốn nhập thủ công
    
    def save(self, *args, **kwargs):
        if not self.slug: # Chỉ tạo slug nếu nó chưa được đặt (ví dụ: khi tạo mới)
            self.slug = slugify(self.title)
        super().save(*args, **kwargs) # Gọi phương thức save gốc để lưu đối tượng
    
    def __str__(self):
        return self.title

class Student(models.Model):
    student_id=models.CharField(max_length=20,unique=True,primary_key=True)
    fullname=models.CharField(max_length=50)
    email=models.EmailField(unique=True)    
    courses=models.ManyToManyField('Course',related_name='students')
    exercises=models.ManyToManyField('Exercise',through='ResultExercise',related_name='students_done')
    
    def __str__(self):
         return f'{self.fullname} | {self.student_id}'

class Account_Student(models.Model):
    user_name=models.CharField(max_length=50,unique=True,primary_key=True)
    password=models.CharField(max_length=20,validators=[MinLengthValidator(8)])
    student=models.OneToOneField(Student, on_delete=models.CASCADE,related_name='account')

class LogFile_Student(models.Model):
    log_file = models.CharField(
    max_length=255,
    unique=True,
    help_text="Khóa đối tượng (object key) của file log trao đổi với AI trên GCS.")
    student=models.OneToOneField(Student, on_delete=models.CASCADE,related_name='log') 

class ResultExercise(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    
    #tạo ra drop menu
    STATUS_CHOICES = [
        ('in_process', 'Đang làm'),
        ('complete', 'Hoàn thành'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, # <-- choices được sử dụng ở đây
        default='in_process',
        null=False,
        blank=False
    )
    
    score = models.IntegerField( validators=[
            MinValueValidator(0, message="Điểm không được nhỏ hơn 0."),
            MaxValueValidator(10, message="Điểm không được lớn hơn 10.")],
            null=True, blank=True) 
    
    submission_date = models.DateTimeField(null=True, blank=True) # Thời gian sinh viên nộp/hoàn thành

    class Meta:
        unique_together = ('student', 'exercise')
 


