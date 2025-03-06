from django.urls import path
from .views import upload_videos, register, user_login, user_logout, payment_success, payment_cancel, plan_list, subscribe, create_checkout_session, stripe_webhook, plans_view

urlpatterns = [
    path("upload/", upload_videos, name="upload_videos"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path('checkout/<int:plan_id>/', create_checkout_session, name='checkout_session'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
    path('plans/', plan_list, name='plan_list'),
    path('plans_view/', plans_view, name='plans_view'),
    path('subscribe/<int:plan_id>/', subscribe, name='subscribe'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
