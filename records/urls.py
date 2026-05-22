from django.urls import path
from records import views

urlpatterns = [
    path('records',views.RecordsViewSet.as_view({'get':'get'})),
    path('records/<str:pk>',views.SingleRecordViewSet.as_view({'get':'retrieve', 'post':'post'})),
    path('records/medic/<str:pk>',views.SingleRecordViewSet.as_view({'post':'post_medic_info', 'get':'get_medic_info'})),
    path('records/detention/<str:pk>',views.SingleRecordViewSet.as_view({'post':'post_detention_info', 'get':'get_detention_info' })),
    path('records/detention/<str:pk>/qualify',views.SingleRecordViewSet.as_view({'post':'qualify_detention'})),
    path('records/cell/<str:pk>',views.SingleRecordViewSet.as_view({'post':'assign_cell', 'get':'get_cell_info'})),
    path('records/belongings/<str:pk>',views.SingleRecordViewSet.as_view({'post':'register_belongings'})),
    path('records/belongings/<str:pk>/print/',views.PrintRecordViewSet.as_view({'put':'print_belongings_info'})),
    path('records/belongings/<str:pk>/deliver',views.SingleRecordViewSet.as_view({'post':'deliver_belongings'})),

    path('records/calls/<str:pk>',views.SingleRecordViewSet.as_view({'post':'register_calls'})),
    path('records/medic/<str:pk>/lesions',views.SingleRecordViewSet.as_view({'post':'post_lesions_info'})),
    path('records/medic/<str:pk>/print/',views.PrintRecordViewSet.as_view({'get':'print_medic_info'})),
    path('records/calls/<str:pk>/print/',views.PrintRecordViewSet.as_view({'get':'print_call_info'})),
    path('records/<int:pk>/actions/',views.ActionsViewSet.as_view({'get':'retrieve','put':'add'})),
    path('records/<int:pk>/actions/print/',views.ActionsPrintViewSet.as_view({'get':'print_action'})),
    path('records/search/', views.AdvancedSearchViewSet.as_view({'post':'search'})),
    path('records/other/search/', views.SearchOtherRecordsViewSet.as_view({'post':'search'})),
    path('records/other_records/',views.OtherRecordsViewSet.as_view({'get':'retrieve', 'post':'add'})),
    path('records/other_records/<int:pk>',views.SingleOtherRecordsViewSet.as_view({'get':'retrieve', 'put':'update'})),
    #path('records/<str:pk>/actions/', views.ActionsViewSet.as_view({'get':'retrieve'}), name='record-actions')
]
