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
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from django.db.utils import IntegrityError
from .models import BlacklistedToken


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
    
            user = serializer.save()

            token = default_token_generator.make_token(user)

            current_site = get_current_site(request).domain
            verification_url = f"http://{current_site}{reverse('verify_email')}?token={token}&email={user.email}"
            
       
            send_mail(
                'Email Verification',
                f'Click the link to verify your email: {verification_url}',
                settings.EMAIL_HOST_USER, 
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
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.auth  
            if not token:
                return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            if BlacklistedToken.objects.filter(token=str(token)).exists():
                return Response({"error": "Token already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)

            BlacklistedToken.objects.create(token=str(token))

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
