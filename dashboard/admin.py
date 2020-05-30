from django.contrib import admin

from dashboard.models import CategoriesStalls, StallsAudience, StallsProducts, Stall, StallFacilities, StallUpload,Users, Articles2, PackageSales, ExpectationsFeedbacks, TicketsSale, AboutCountries, Leads
from .models import Admin
# Register your models here.
admin.site.register(Admin)


admin.site.register(CategoriesStalls)
admin.site.register(StallsAudience)
admin.site.register(StallsProducts)
admin.site.register(Stall)
admin.site.register(StallFacilities)
admin.site.register(StallUpload) 
admin.site.register(Users)  
admin.site.register(Articles2) 
admin.site.register(PackageSales) 
admin.site.register(ExpectationsFeedbacks) 
admin.site.register(TicketsSale)
admin.site.register(AboutCountries)
admin.site.register(Leads)