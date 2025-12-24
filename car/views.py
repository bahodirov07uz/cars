import requests
from django.shortcuts import render,redirect
from django.views.generic import ListView,FormView,DetailView,TemplateView
from decouple import config
from django.core.mail import send_mail
from django.db.models import Min,Max
from django.conf import settings
from django.urls import reverse_lazy
from django.template import Template, RequestContext

from .models import VehicleImage,Vehicle,Feature,SiteInfo,Aboutpage,IndexModel,ShippingPage,Privacy,TermsOfUse
from .forms import ContactForm


TELEGRAM_BOT_TOKEN =config("BOT_TOKEN")
TELEGRAM_CHAT_ID = config("CHANNEL_ID")

class HomeView(ListView):
    template_name = "index.html"
    model = Vehicle
    context_object_name = 'cars'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter parametrlarini olish
        make = self.request.GET.get('make')
        year = self.request.GET.get('year')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        # Filter qo'llash
        if make and make != 'all':
            queryset = queryset.filter(make=make)
        
        if year and year != 'all':
            # Year range format: "2020-2025" yoki "2020"
            if '-' in year:
                start_year, end_year = year.split('-')
                queryset = queryset.filter(year__gte=start_year, year__lte=end_year)
            else:
                queryset = queryset.filter(year=year)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = SiteInfo.objects.all().first()
        
        # Filter uchun ma'lumotlarni tayyorlash
        vehicles = Vehicle.objects.all()

                
        makes = vehicles.values_list('brand', flat=True).distinct()
        context['makes'] = makes
        
         # Mavjud yillar ni olish va guruhlash
        years = vehicles.values_list('year', flat=True).distinct().order_by('year')
        
        # Yillarni guruhlash (masalan: 1950-1959, 1960-1969)
        year_ranges = []
        if years:
            min_year = years.first()
            max_year = years.last()
            
            # Har 10 yillik interval uchun
            for decade_start in range(min_year // 10 * 10, max_year + 10, 10):
                decade_end = decade_start + 9
                decade_years = [year for year in years if decade_start <= year <= decade_end]
                if decade_years:
                    year_ranges.append({
                        'range': f"{decade_start}-{decade_end}",
                        'count': len(decade_years)
                    })

        page = IndexModel.objects.first()

        if page:
            tpl = Template(page.code)
            rendered_html = tpl.render(RequestContext(self.request, context))
            context['rendered_code'] = rendered_html
        else:
            context['rendered_code'] = ''

        context['year_ranges'] = year_ranges
        context['all_years'] = list(years)  # Alohida yillar ham kerak bo'lsa
        
        # Narxlar uchun min va max qiymatlarni olish
        price_range = vehicles.aggregate(min_price=Min('price'), max_price=Max('price'))
        context['min_price_value'] = price_range['min_price'] or 0
        context['max_price_value'] = price_range['max_price'] or 100000
        context['code'] = IndexModel.objects.first()
        # Joriy filter parametrlarini saqlash
        context['current_make'] = self.request.GET.get('make', 'all')
        context['current_year'] = self.request.GET.get('year', 'all')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        
        return context
    
class CarDetailView(DetailView):
    model = Vehicle
    template_name = "vehicle.html"
    context_object_name = "car"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = self.object.images.all()  # Ko‘p rasm
        return context


class ContactView(FormView):
    template_name = "index.html"
    form_class = ContactForm

    def form_valid(self, form):
        contact = form.save(commit=False)

        # Agar url da car_id bo‘lsa — avtomatik ulanadi
        car_id = self.kwargs.get("car_id")
        if car_id:
            from .models import Vehicle  
            try:
                contact.car = Vehicle.objects.get(id=car_id)
            except Vehicle.DoesNotExist:
                pass

        contact.save()

        # --- Send Telegram ---
        text = f"📩 New Contact Request\n" \
               f"Name: {contact.name}\n" \
               f"Email: {contact.email}\n" \
               f"Phone: {contact.phone}\n" \
               f"Message: {contact.message}\n"

        if contact.car:
            text += f"\n🚗 Vehicle: {contact.car.title} ({contact.car.year})\nVIN: {contact.car.vin}"

        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            params={"chat_id": TELEGRAM_CHAT_ID, "text": text}
        )

        # --- Send Email ---
        email_message = text.replace("\n", "<br>")
        send_mail(
            subject="New Contact Request",
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["sales@jeautosalesco.com"],
            html_message=email_message,
        )

        return super().form_valid(form)
   
    def get_success_url(self):
        return reverse_lazy('car:thank_you')



class ThankYouView(TemplateView):
    template_name = 'thank-you.html'
    
class AboutPage(ListView):
    template_name = 'about.html'
    model = Aboutpage
    context_object_name = "about"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['ab'] = Aboutpage.objects.all().first()
        
        page = Aboutpage.objects.first()

        if page:
            tpl = Template(page.code)
            rendered_html = tpl.render(RequestContext(self.request, context))
            context['rendered_code'] = rendered_html
        else:
            context['rendered_code'] = ''
        return context
    
# class FinanceView(TemplateView):
#     template_name = 'finance.html'

class ShippingView(TemplateView):
    template_name = 'shipping.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        page = ShippingPage.objects.first()

        if page:
            tpl = Template(page.code)
            rendered_html = tpl.render(RequestContext(self.request, context))
            context['rendered_code'] = rendered_html
        else:
            context['rendered_code'] = ''
        return context
    
class PrivacyView(TemplateView):
    template_name = 'privacy.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        page = Privacy.objects.first()

        if page:
            tpl = Template(page.code)
            rendered_html = tpl.render(RequestContext(self.request, context))
            context['rendered_code'] = rendered_html
        else:
            context['rendered_code'] = ''
        return context
    
    
class TermsOfUseView(TemplateView):
    template_name = 'termsofuse.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        page = TermsOfUse.objects.first()

        if page:
            tpl = Template(page.code)
            rendered_html = tpl.render(RequestContext(self.request, context))
            context['rendered_code'] = rendered_html
        else:
            context['rendered_code'] = ''
        return context
    