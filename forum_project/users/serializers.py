from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import MyUser
from django.core.mail import send_mail
import logging
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

MyUser = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = MyUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        email = validated_data.get("email")

        if MyUser.objects.filter(email=email).exists():
            logger.warning(f"User with email {email} already exists.")  
            raise ValidationError({"email": ["User with this email already exists."]})

        validated_data.pop("confirm_password", None)

        user = MyUser.objects.create_user(
            email=validated_data.pop('email'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            password=validated_data.pop('password'),
            **validated_data 
            
        )

        user.is_active = False  # User needs to verify email
        user.save()

        logger.info(f"User created successfully: {email}")  # Log success
        return user

        
    
