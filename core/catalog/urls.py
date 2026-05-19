from django.urls import path, include

app_name = 'catalog'


urlpatterns = [
     path("api/v1/",include('catalog.api.v1.urls'), name='api-v1'),
]