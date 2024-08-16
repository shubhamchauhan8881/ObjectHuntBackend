from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from . import models
from PIL import Image
from io import BytesIO
import base64


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name")
    class Meta:
        model = User
        fields = ("username", "name")
        extra_kwargs = {'first_name': {'required': True}}
        
    def create(self, validated_data):
        user = User.objects.create(
            username= validated_data['username'],
            first_name=validated_data['first_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.first_name
        token['username'] = user.username
        return token


class ImageRes:
    def __init__(self,prompt, image):
        self.prompt = prompt
        self.image = image
    @property
    def get_image(self):
        return Image.open(BytesIO(base64.b64decode(self.image.split("data:image/jpeg;base64,")[1])))


class ImagePromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length = 200, required=True)
    image = serializers.CharField(required=True)

    def create(self, validated_data):
        return ImageRes(**validated_data)


class CreateRoomSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    class Meta:
        model = models.Room
        fields = '__all__'
        depth = 1
