from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, OTP
from .services import generate_otp_code

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name', 'is_2fa_enabled')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_2fa_enabled=validated_data.get('is_2fa_enabled', False)
        )

        if user.is_2fa_enabled:
            otp_code = generate_otp_code()
            OTP.objects.create(user=user, code=otp_code)
            print(f"OTP для {user.email}: {otp_code}")

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_2fa_enabled')
        read_only_fields = ('email',)


class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, help_text="Введите 6-значный код OTP")

