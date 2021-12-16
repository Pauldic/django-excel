from django.conf.urls import include, url
from django.contrib import admin
from core.views import site_work_summary
from core.views import list_invoices
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', list_invoices, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^core/', include('core.urls'))
]
# admin.site.register('admin/core/task/site/work/summary/', site_work_summary)


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
