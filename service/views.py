from service.models import Kafic
from service.serializers import KaficSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from service.permissions import IsOwnerOrReadOnly


class ListaKafica(generics.ListAPIView):
    queryset = Kafic.objects.all()
    serializer_class = KaficSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user


class KaficDetalji(generics.RetrieveUpdateDestroyAPIView):
    queryset = Kafic.objects.all()
    serializer_class = KaficSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer