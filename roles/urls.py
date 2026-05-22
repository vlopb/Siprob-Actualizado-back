from django.urls import path, include
from rest_framework.routers import DefaultRouter
from roles import views

# router = DefaultRouter()
# router.register(r'roles',RoleViewSet,basename='Role')
urlpatterns =[
    path('roles',views.RolesViewSet.as_view({'get':'get','post':'post'})),
    path('roles/<int:pk>',views.SingleRoleViewSet.as_view({'get':'retrieve','delete':'destroy','put':'update'}))
]


# urlpatterns = [
#     # path('',RolesListViewSet.as_view()),
#     # path('',CreateRoleView.as_view(), name='Delete'),
#     path('<int:pk>',RoleViewSet.as_view()),
#     # path('<int:pk>', ShowRoleView.as_view(), name='Show')
# ]
