from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

FUEL_CHOICES = [
    ("gasoline", "Gasoline"),
    ("diesel", "Diesel"),
    ("electric", "Electric"),
    ("hybrid", "Hybrid"),
    ("other", "Other"),
]

DRIVETRAIN_CHOICES = [
    ("rwd", "RWD"),
    ("fwd", "FWD"),
    ("awd", "AWD"),
    ("4wd", "4WD"),
    ("other", "Other"),
]

BODY_STYLE_CHOICES = [
    ("sedan", "Sedan"),
    ("hatchback", "Hatchback"),
    ("coupe", "Coupe"),
    ("convertible", "Convertible"),
    ("pickup", "Pickup Truck"),
    ("wagon", "Wagon"),
    ("suv", "SUV"),
    ("other", "Other"),
]


class Feature(models.Model):
    """
    Vehicle features (examples: 'Classic Forrest Green paint', 'Wood bed floor', etc.)
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="feature name")
    description = models.TextField(blank=True, null=True, verbose_name="feature description")

    class Meta:
        ordering = ["name"]
        verbose_name = "Feature"
        verbose_name_plural = "Features"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name

# --- Vehicle model ---
class Vehicle(models.Model):
    """
    Main vehicle model for listings like Bel Air Restomod.
    """
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="title")
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="price (USD)")
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True, verbose_name="mileage (mi)")
    engine = models.CharField(max_length=255, blank=True, null=True, verbose_name="engine")
    year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="year")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Location")
    transmission = models.CharField(max_length=100, blank=True, null=True, verbose_name="transmission")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, blank=True, null=True, verbose_name="fuel type")
    drivetrain = models.CharField(max_length=10, choices=DRIVETRAIN_CHOICES, blank=True, null=True, verbose_name="drivetrain")
    body_style = models.CharField(max_length=50, choices=BODY_STYLE_CHOICES, blank=True, null=True, verbose_name="body style")
    exterior_color = models.CharField(max_length=100, blank=True, null=True, verbose_name="exterior color")
    interior_color = models.CharField(max_length=100, blank=True, null=True, verbose_name="interior color")
    vin = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="VIN")
    stock_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="stock number")
    description = models.TextField(blank=True, null=True, verbose_name="vehicle description")
    features = models.ManyToManyField(Feature, blank=True, related_name="vehicles", verbose_name="features")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    # flexible extra fields for future use (null & blank true)
    extra_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name="extra field 1")
    extra_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="extra field 2")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        indexes = [
            models.Index(fields=["vin"]),
            models.Index(fields=["stock_number"]),
            models.Index(fields=["year"]),
        ]

    def __str__(self):
        if self.title:
            return f"{self.title} ({self.year or 'n/a'})"
        return f"Vehicle {self.pk} - {self.vin or 'no-vin'}"

    def clean(self):
        # Validate number of images not exceeding 20
        # Note: this will work when related VehicleImage instances are available in memory (e.g., in admin forms).
        max_images = 20
        if self.pk:
            images_count = self.images.count()
            if images_count > max_images:
                raise ValidationError(_("A vehicle cannot have more than %(max)d images."), params={"max": max_images})

    def get_primary_image(self):
        first = self.images.order_by("order").first()
        return first.image.url if first and first.image else None

    def features_list(self):
        return ", ".join(f.name for f in self.features.all())
    features_list.short_description = "Features"


# --- Vehicle images (many images per vehicle) ---
def vehicle_image_upload_to(instance, filename):
    # organizes uploads by vehicle id
    return f"vehicles/{instance.vehicle.id if instance.vehicle_id else 'unknown'}/{filename}"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images", verbose_name="vehicle")
    image = models.ImageField(upload_to=vehicle_image_upload_to, blank=True, null=True, verbose_name="image file")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="caption")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="display order")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="uploaded at")

    class Meta:
        ordering = ["order", "-uploaded_at"]
        verbose_name = "Vehicle Image"
        verbose_name_plural = "Vehicle Images"

    def __str__(self):
        return f"Image {self.pk} for Vehicle {self.vehicle_id}"

class Contacts(models.Model):
    phone = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
    work_days = models.CharField(max_length=600)
    
class Contact(models.Model):
    car = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="contacts",
        verbose_name="related vehicle",
    )
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="user name")
    email = models.EmailField(blank=True, null=True, verbose_name="user email")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="phone number")
    message = models.TextField(blank=True, null=True, verbose_name="message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="submitted at")

    class Meta:
        verbose_name = "Contact Request"
        verbose_name_plural = "Contact Requests"
        ordering = ['-created_at']

    def __str__(self):
        if self.car:
            return f"Contact for {self.car.title or self.car.pk} ({self.email})"
        return f"General Contact – {self.email}"

class SiteInfo(models.Model):
    site_name = models.CharField(max_length=255, blank=True, null=True)
    banner = models.ImageField(upload_to="sitesettings",null=True)
    logo = models.ImageField(upload_to="sitesettings",null=True)
    showroom_iframe = models.TextField()
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    location = models.TextField( blank=True, null=True)
    opening_hours = models.TextField( blank=True, null=True)
    video = models.FileField(upload_to="sitesettings/videos")
    
class Aboutpage(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField( blank=True, null=True)
    banner = models.ImageField(upload_to="sitesettings/about",null=True)