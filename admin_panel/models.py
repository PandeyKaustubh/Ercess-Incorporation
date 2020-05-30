from django.db import models

choice = (
    ('','Select Option'),
    ('1','Male'),
    ('2','Female')
)



# class AddUser(models.Model):
#     first_name = models.CharField(max_length = 100)
#     last_name = models.CharField(max_length = 100)
#     email = models.EmailField()
#     gender = models.CharField(max_length = 20,choices = choice)
#     location = models.CharField(max_length = 100)
#     mobile_no = models.CharField(max_length = 10,blank = True,null = True)
#     organization = models.CharField(max_length = 100,blank = True,null = True)
#     password = models.CharField(max_length = 50)
#     md5 = models.CharField(max_length = 100)

#     class Meta:
#         db_table = 'add_user'
        
