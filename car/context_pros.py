from .models import SiteInfo

def logocon(request):
    return {"site":SiteInfo.objects.all().first()}