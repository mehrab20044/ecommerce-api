from django.urls import path , include
from  rest_framework.routers import DefaultRouter
from .views import *

app_name = 'api-v1'

router= DefaultRouter()
router.register('product',ProductViewSet,basename='product')
router.register('category',CategoryViewSet,basename='category')
urlpatterns = router.urls