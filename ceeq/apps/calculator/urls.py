from django.conf.urls import url

from ceeq.apps.calculator import views

urlpatterns = [
    url(r'^$', views.calculate_score_all, name='calculate_score_all'),
]
