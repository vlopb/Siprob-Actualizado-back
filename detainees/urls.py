from django.urls import path
from detainees import views

urlpatterns = [
    path('',views.DetaineesViewSet.as_view({'get':'get','post':'post'})),
    path('<int:pk>',views.SingleDetaineeViewSet.as_view({'get':'retrieve', 'put':'update', 'post':'release'})),
    path('<int:pk>/release',views.SingleDetaineeViewSet.as_view({'put':'release'}))
]
