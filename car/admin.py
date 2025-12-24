from django.contrib import admin
from .models import Vehicle, Feature, VehicleImage,Contact,SiteInfo,Brand,Aboutpage,IndexModel,ShippingPage,Privacy,TermsOfUse
from django.contrib.admin import AdminSite,ModelAdmin

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
# pages

class PagesModelAdmin(ModelAdmin):
    # Umumiy sozlamalar
    list_display = ['__str__']
    list_per_page = 20

# Har bir model uchun alohida admin class
@admin.register(SiteInfo)
class SiteInfoAdmin(PagesModelAdmin):
    pass

@admin.register(Brand)
class BrandAdmin(PagesModelAdmin):
    pass

@admin.register(Aboutpage)
class AboutpageAdmin(PagesModelAdmin):
    pass

@admin.register(ShippingPage)
class ShippingPageAdmin(PagesModelAdmin):
    pass

@admin.register(TermsOfUse)
class TermsOfUseAdmin(PagesModelAdmin):
    pass

@admin.register(Privacy)
class PrivacyAdmin(PagesModelAdmin):
    pass

@admin.register(IndexModel)
class IndexModelAdmin(ModelAdmin):
    pass

# Admin panelda app nomini o'zgartirish
from django.apps import apps

# Car app ni Pages deb nomlash
app_config = apps.get_app_config('car')
app_config.verbose_name = "Pages"

# Har bir model uchun nomlarni o'zgartirish
SiteInfo._meta.verbose_name = "Site Info"
SiteInfo._meta.verbose_name_plural = "Site Infos"

Brand._meta.verbose_name = "Brand"
Brand._meta.verbose_name_plural = "Brands"

Aboutpage._meta.verbose_name = "About"
Aboutpage._meta.verbose_name_plural = "About"

ShippingPage._meta.verbose_name = "Shipping"
ShippingPage._meta.verbose_name_plural = "Shipping"

TermsOfUse._meta.verbose_name = "Terms of Use"
TermsOfUse._meta.verbose_name_plural = "Terms of Use"

Privacy._meta.verbose_name = "Privacy"
Privacy._meta.verbose_name_plural = "Privacy"

IndexModel._meta.verbose_name = "Home Page"
IndexModel._meta.verbose_name_plural = "Home Pages"