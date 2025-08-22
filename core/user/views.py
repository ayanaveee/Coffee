from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import login
from .models import User, OTP
from .serializers import UserRegisterSerializer, UserProfileSerializer, OTPSerializer

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class OTPVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, user_id):
        user = generics.get_object_or_404(User, id=user_id)
        otp_code = request.data.get('otp')

        if not otp_code:
            return Response({'detail': 'OTP не передан'}, status=status.HTTP_400_BAD_REQUEST)

        otp = OTP.objects.filter(user=user, code=otp_code).last()
        if otp:
            otp.delete()
            login(request, user)
            return Response({'detail': 'OTP подтверждён'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Неправильный код'}, status=status.HTTP_400_BAD_REQUEST)
