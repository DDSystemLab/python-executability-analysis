from django.conf.urls import url
from django.urls import include

from . import views

app_name = 'python_snippets'

urlpatterns = [
    url(r"^get_new_task/(?P<python_version>\d+)", views.get_new_task, name='get_new_task'),
    url(r"^update_task/(?P<python_version>\d+)", views.update_task, name='update_task'),
    url(r"^get_task/(?P<pk>\d+)", views.get_task, name='get_task'),
    url(r"^clear_everything/$", views.clear_everything, name='clear_everything'),
]
