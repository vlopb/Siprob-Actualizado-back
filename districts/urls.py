from django.urls import path, include
from rest_framework.routers import DefaultRouter
from districts import views
# from districts.views import DistrictViewSet

# router = DefaultRouter()
# router.register(r'districts',DistrictViewSet,basename='District')
urlpatterns =[
    path('<int:pk>',views.DistrictViewSet.as_view({'get':'retrieve','delete':'destroy','put':'update'})),
    path('',views.DistrictViewSet.as_view({'get':'list'}))
]

# urlpatterns = [
# ]
