from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('zones/', views.multi_zone_view, name='multi_zone'),
    path('report/<int:record_id>/pdf/', views.export_pdf_report_view, name='export_pdf_report'),
    path('api/weather/', views.weather_proxy_view, name='weather_proxy'),
    path('api/locations/', views.search_locations_api_view, name='search_locations_api'),
    path('api/optimize-zone/', views.optimize_zone_api_view, name='optimize_zone_api'),
    path('history/', views.history_view, name='history'),
    path('methodology/', views.research_view, name='research'),
]
