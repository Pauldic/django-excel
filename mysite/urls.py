from django.conf.urls import include, url
from django.contrib import admin
from core.views import site_work_summary
from core.views import list_invoices


urlpatterns = [
    url(r'^$', list_invoices, ),
    url(r'^admin/', admin.site.urls),
    url(r'^core/', include('core.urls'))
]

# admin.site.register('admin/core/task/site/work/summary/', site_work_summary)