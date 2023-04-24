from django.urls import path
from .views_api import *

urlpatterns = [
    path('login/', LoginView),
    path('register/', RegisterView),
    # path('forget-password/' , ForgetPasswordView, name="forget_password"),
    # path('change-password/<token>/' , ChangePasswordView , name="change_password"),
    
]
