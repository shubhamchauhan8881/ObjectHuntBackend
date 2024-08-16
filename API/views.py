from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import genAi
import json
from . import models
import random


from rest_framework_simplejwt.authentication import JWTAuthentication
class UserRegister(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        form = serializers.UserSerializer(data = request.data )
        if form.is_valid():
            form.save()
            return Response(form.data, status=status.HTTP_201_CREATED)
        else:
            return Response( form.errors, status = status.HTTP_400_BAD_REQUEST)


class RecognizeImage(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        f = serializers.ImagePromptSerializer(data = request.data)
        if f.is_valid():
            res = f.save()
            genai = genAi.Generator(api_key="AIzaSyALFj-pOmdaeqHc3BWVnmiMQL1bBkNS1Xg")
            res = genai.recognizeObject(prompt=res.prompt, image = res.get_image)
            res = json.loads(res)[0]
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response(f.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoom(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        roomid = ""
        while True:
            roomid = random.randrange(100000, 999999)
            # check if room is already created with room_id
            if not models.Room.objects.filter(room_id=roomid).exists():
                break
        room = models.Room.objects.create(room_id=roomid, owner=request.user)

        rom = serializers.CreateRoomSerializer(room)
        return Response(rom.data, status=status.HTTP_201_CREATED)


def chat(request):
    return render(request,"index.html")


class ValidateRoomCode(APIView):
    def get(self, request, code):
        data = {"ok":True}
        if not(models.Room.objects.filter(room_id=code).exists()):
            data["ok"] = False
        return Response(data=data)