from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .serializers import RegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
    
            user = serializer.save()

            token = default_token_generator.make_token(user)

            # Get the current domain (this would be your domain, e.g., example.com)
            # current_site = get_current_site(request).domain

            # Create the verification URL for us use localhost now
            verification_url = f"http://127.0.0.1:8000/verify-email/?token={token}&email={user.email}"
            
       
            send_mail(
                'Email Verification',
                f'Click the link to verify your email: {verification_url}',
                'workexample706@gmail.com', 
                [user.email],  
                fail_silently=False,
            )

            return Response({"message": "User registered successfully. Please check your email for verification."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        email = request.query_params.get('email')

        if token and email:
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response({"message": "User does not exist."}, status=400)


            if default_token_generator.check_token(user, token):
                user.is_active = True  
                user.save()

                return Response({"message": "Email verified successfully"}, status=200)
            else:
                return Response({"message": "Invalid or expired token"}, status=400)

        return Response({"message": "Invalid request"}, status=400)
