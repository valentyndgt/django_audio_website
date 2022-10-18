from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .utils import send_email_account_activation, send_email_password_reset
from .models import Profile
from .serializers import UserSerializer, InputEmailSerializer, ProfileSerializer


class ApiSignUpView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    user_model = get_user_model()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = self.user_model(
            email=email,
            username=serializer.validated_data['username'],
        )
        user.set_password(serializer.validated_data['password'])
        user.is_active = False
        user.save()
        send_email_account_activation(self.request, user, email)

        headers = self.get_success_headers(serializer.validated_data)
        data = serializer.data
        data['msg'] = 'Account created, but it is inactive until activation link is clicked. ' \
                       'Email with account activation link has been sent.'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class ApiPasswordResetView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = InputEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_email = serializer.validated_data['email']
        user_model = get_user_model()
        user = user_model.objects.filter(email=to_email, is_active=True).first()
        if user is not None:
            send_email_password_reset(request, user, to_email)
        return Response({'msg': 'Email with password reset link has been sent '
                                 '(If account with email exists).'}, status=status.HTTP_200_OK)


class ApiProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = Profile.objects.all()

    def get_object(self):
        return get_object_or_404(self.queryset, user=self.request.user)
