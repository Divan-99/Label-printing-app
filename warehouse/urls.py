from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('',              views.search_view,       name='search'),
    path('autocomplete/', views.autocomplete_view,  name='autocomplete'),
    path('print/',        views.print_label_view,   name='print_label'),
    path('ping/',         views.ping_printer_view,  name='ping_printer'),
]
