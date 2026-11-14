from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('zones/', views.multi_zone_view, name='multi_zone'),
    path('community/', views.community_hub_view, name='community_hub'),
    path('api/community/posts/', views.community_create_post_api, name='community_create_post_api'),
    path('api/community/posts/<int:post_id>/reply/', views.community_reply_api, name='community_reply_api'),
    path('api/community/posts/<int:post_id>/upvote/', views.community_upvote_api, name='community_upvote_api'),
    path('api/community/chat/', views.community_chat_api, name='community_chat_api'),
    path('report/<int:record_id>/pdf/', views.export_pdf_report_view, name='export_pdf_report'),
    path('calendar/<int:record_id>/ics/', views.export_ics_calendar_view, name='export_ics_calendar'),
    path('api/agronomist-chat/', views.agronomist_chat_api_view, name='agronomist_chat_api'),
    path('api/weather/', views.weather_proxy_view, name='weather_proxy'),
    path('api/locations/', views.search_locations_api_view, name='search_locations_api'),
    path('api/optimize-zone/', views.optimize_zone_api_view, name='optimize_zone_api'),
    path('history/', views.history_view, name='history'),
    path('methodology/', views.research_view, name='research'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('api/auth/send-otp/', views.send_registration_otp_api, name='send_registration_otp_api'),
    path('api/auth/verify-otp/', views.verify_registration_otp_api, name='verify_registration_otp_api'),
    path('api/diagnose-leaf/', views.leaf_doctor_api_view, name='leaf_doctor_api'),
    path('api/ndvi-satellite/', views.ndvi_satellite_api_view, name='ndvi_satellite_api'),
    path('presentation/', views.presentation_view, name='presentation'),
    path('presentation/download/', views.download_presentation_pptx, name='download_presentation'),
]
