from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class SignInView(APIView):
    def post(self, request):
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        credentials = {username_field: request.data.get(username_field)}
        password = request.data.get('password')

        if not request.data.get(username_field) or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(**credentials, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "message": "Login successful",
            "user": getattr(user, username_field, user.email),
            "access_token": access_token,
        })
        response.set_cookie('refresh_token', str(refresh), httponly=True)
        return response

