from django.contrib import admin
from  Ercesscorp.models import RegistrationData ,BlogData
# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','author')
    list_filter = ('title','author')
    fieldsets = (

        ('Blog Information', {
            'classes': ('collapse',),
            'fields': ('title','author','image', 'description','date')
        }),


    )

admin.site.register(RegistrationData)
admin.site.register(BlogData , BlogAdmin)