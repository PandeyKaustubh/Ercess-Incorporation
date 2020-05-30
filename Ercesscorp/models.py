from django.db import models
from django.contrib.auth.models import  User
choice = (
    ('','Gender'),
    ('1','Male'),
    ('2','Female')
)



class RegistrationData(models.Model):
    user = models.OneToOneField(User, related_name='reg' , on_delete=models.DO_NOTHING)
    # mobile = models.BigIntegerField()
    gender = models.CharField(max_length=10 , default='blank' )
    location = models.CharField(max_length=30 , default='blank')
    submitted = models.IntegerField(default=0)
    how_u_know = models.CharField(max_length=100 , default='other')
    verify = models.IntegerField(default=0)





class BlogData(models.Model):
    blog_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=50 )
    title  = models.CharField(max_length=100)
    description = models.TextField()
    image = models.FileField(upload_to='images',default='images/business-events-cover-1.jpg' )
    date = models.DateTimeField()
    def __str__(self):
        return  self.title


class ContactData(models.Model):
    username = models.CharField(max_length=100 , null=False)
    email  = models.EmailField(max_length=70 , null=False)
    mobile = models.BigIntegerField(null=False)
    purpose = models.CharField(max_length=20, null=False)
    comment = models.CharField(max_length=1000 , null=False)
    def __str__(self):
        return  self.username

class Users(models.Model):
    social_userid = models.TextField(blank=True, null=True)
    md5 = models.CharField(max_length=300)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    user = models.CharField(max_length=40)
    profile_pic = models.TextField()
    gender = models.CharField(max_length=8)
    location = models.CharField(max_length=25)
    mobile = models.CharField(max_length=11,blank = True,null = True)
    password = models.CharField(max_length=300, blank=True, null=True)
    mobile_verified = models.IntegerField(default=0)
    status = models.CharField(max_length=8, default='pending')
    first_time = models.CharField(max_length=10)
    organization_name = models.CharField(max_length=200,blank = True,null = True)
    organization_location = models.TextField()

    class Meta:
        managed = False
        db_table = 'users'

class UserRegistrationToken(models.Model):
    user_email_token = models.CharField(max_length=250, default='')
    user_email_token_created_on = models.DateTimeField(null=True,blank=True)
    user_password_token = models.CharField(max_length=250, default='')
    user_email = models.CharField(max_length=250, default='')
    user_password_token_created_on = models.DateTimeField(null=True,blank=True)
