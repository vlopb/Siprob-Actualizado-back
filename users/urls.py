from django.urls import path
from users import views

urlpatterns = [
    # path('',views.ListUsersView.as_view()),
    # path('create/',views.CreateUserView.as_view()),
    path('users/in/',views.CreateTokenView.as_view({'post':'post'})),
    path('users/',views.UsersViewSet.as_view({'get':'get','post':'post'})),
    path('users/search/',views.SearchUsersViewSet.as_view({'post':'search'})),
    path('users/seed/',views.SeederUserView.as_view({'post':'seed_data'})),
    path('users/<int:pk>',views.SingleUserView.as_view({'get':'retrieve','delete':'destroy','put':'update'})),
    #path('users/<int:pk>',views.UpdateUserView.as_view({'put':'update'})),
    path('users/change_password/',views.ShowUserView.as_view({'post':'change_password'})),
    path('users/reset_password/',views.PasswordRecoverViewSet.as_view({'post':'send_email'})),
    # path('roles/',views.CreateRoleView.as_view()),
    # path('roles/',views.ListRolesView.as_view())
]
