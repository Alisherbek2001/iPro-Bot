# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class UserDetailCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        telegram_id = self.kwargs.get('telegram_id')
        try:
            return User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise NotFound(detail="Foydalanuvchi topilmadi", code=404)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        language = request.data.get('language')
        if language:
            user.language = language
            user.save()
            return Response({"message": "Til yangilandi", "language": user.language},status=status.HTTP_200_OK)
        return Response({"error": "Til ma'lumotlari yetarli emas"}, status=status.HTTP_400_BAD_REQUEST)