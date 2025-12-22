from django.contrib import admin
from .models import Vehicle, Feature, VehicleImage,Contact,SiteInfo,Brand,Aboutpage

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    fields = ("image", "caption", "order",)
    readonly_fields = ()
    max_num = 20  # prevent admins uploading > 20 images from admin
    verbose_name = "Vehicle Image"
    verbose_name_plural = "Vehicle Images"


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("__str__", "price", "mileage", "year", "vin", "stock_number")
    search_fields = ("vin", "stock_number", "title", "exterior_color", "interior_color")
    list_filter = ("year", "fuel_type", "drivetrain", "body_style")
    inlines = [VehicleImageInline]
    filter_horizontal = ("features",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "caption", "order", "uploaded_at")
    search_fields = ("vehicle__vin", "caption")

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "car", "created_at")
    list_filter = ("created_at", "car")
    search_fields = ("name", "email", "phone", "message")
    
admin.site.register(SiteInfo)
admin.site.register(Brand)
admin.site.register(Aboutpage)