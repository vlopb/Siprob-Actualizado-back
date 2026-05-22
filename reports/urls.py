from django.urls import path
from reports import views

urlpatterns = [
    path('reports/other_records',views.OtherRecordsViewSet.as_view({'post':'download_other_records'})),
    path('reports/detainees',views.DetaineesViewSet.as_view({'post':'download_detainees'})),        
]