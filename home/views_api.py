from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile
from .helpers import *
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login
from .helpers import send_forget_password_mail
import uuid

class LoginView(APIView):

    def post(self, request):
        response = {}
        response['status'] = 500
        response['message'] = 'Something went wrong'
        try:
            data = request.data

            if data.get('username') is None:
                response['message'] = 'key username not found'
                raise Exception('key username not found')

            if data.get('password') is None:
                response['message'] = 'key password not found'
                raise Exception('key password not found')

            check_user = User.objects.filter(
                username=data.get('username')).first()

            if check_user is None:
                response['message'] = 'invalid username , user not found'
                raise Exception('invalid username not found')

            if not Profile.objects.filter(user=check_user).first().is_verified:
                response['message'] = 'your profile is not verified'
                raise Exception('profile not verified')

            user_obj = authenticate(username=data.get('username'),
                                    password=data.get('password'))
            if user_obj:
                login(request, user_obj)
                response['status'] = 200
                response['message'] = 'Welcome'
            else:
                response['message'] = 'invalid password'
                raise Exception('invalid password')


        except Exception as e:
            print(e)

        return Response(response)


LoginView = LoginView.as_view()


class RegisterView(APIView):

    def post(self, request):
        response = {}
        response['status'] = 500
        response['message'] = 'Something went wrong'
        try:
            data = request.data
            print(data)

            if data.get('username') is None:
                response['message'] = 'key username not found'
                raise Exception('key username not found')

            if data.get('password') is None:
                response['message'] = 'key password not found'
                raise Exception('key password not found')
            check_user = User.objects.filter(
                username=data.get('username')).first()
            if check_user:
                response['message'] = 'username  already taken'
                raise Exception('username  already taken')

            user_obj = User.objects.create(email=data.get('username'),
                                           username=data.get('username'))
            print(user_obj)
            user_obj.set_password(data.get('password'))
            user_obj.save()
            token = generate_random_string(20)
            # set verified user
            Profile.objects.create(user=user_obj, token=token,
                                   is_verified=True)
            # send_mail_to_user(token , data.get('username'))
            response['message'] = 'User created '
            response['status'] = 200
        except Exception as e:
            print(e)

            return Response(response)


RegisterView = RegisterView.as_view()

class ChangePasswordView(APIView):

    def ChangePassword(request , token):
        context = {}
        
        
        try:
            profile_obj = Profile.objects.filter(forget_password_token = token).first()
            context = {'user_id' : profile_obj.user.id}
            
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('reconfirm_password')
                user_id = request.POST.get('user_id')
                
                if user_id is  None:
                    messages.success(request, 'No user id found.')
                    return redirect(f'/change-password/{token}/')
                    
                
                if  new_password != confirm_password:
                    messages.success(request, 'both should  be equal.')
                    return redirect(f'/change-password/{token}/')
                            
                
                user_obj = User.objects.get(id = user_id)
                user_obj.set_password(new_password)
                user_obj.save()
                return redirect('/login/')
                
                
                
            
            
        except Exception as e:
            print(e)
        return render(request , 'change-password.html' , context)
ChangePasswordView = ChangePasswordView.as_view()




class ForgetPasswordView(APIView):
    def ForgetPassword(request):
        try:
            if request.method == 'POST':
                username = request.POST.get('username')
                
                if not User.objects.filter(username=username).first():
                    messages.success(request, 'Not user found with this username.')
                    return redirect('/forget_password/')
                
                user_obj = User.objects.get(username = username)
                token = str(uuid.uuid4())
                profile_obj= Profile.objects.get(user = user_obj)
                profile_obj.forget_password_token = token
                profile_obj.save()
                send_forget_password_mail(user_obj.email , token)
                messages.success(request, 'An email is sent.')
                return redirect('/forget_password/')
                    
        
        
        except Exception as e:
            print(e)
        return render(request , 'forget-password.html')

ForgetPasswordView = ForgetPasswordView.as_view()