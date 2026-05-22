from django.urls import path
from shifts import views
urlpatterns = [
    path('',views.ShiftsViewSet.as_view({'get':'get','post':'post'})),
    path('shifts/<int:pk>',views.SingleShiftViewSet.as_view({'get':'retrieve','delete':'destroy','put':'update'}))
]