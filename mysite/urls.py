from django.conf.urls import include, url
from django.contrib import admin
from core.views import site_work_summary


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^core/', include('core.urls'))
]

# admin.site.register('admin/core/task/site/work/summary/', site_work_summary)