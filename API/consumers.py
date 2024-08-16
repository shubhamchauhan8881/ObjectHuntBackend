from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from . import models
from channels.db import database_sync_to_async
from django.contrib.auth.models import User




@database_sync_to_async
def returnUser(uid):
    return User.objects.get(pk=uid)


# @database_sync_to_async
# def get_user_score(room, user):
#     return 



def get_room_members(room):
    res = []
    for user in room.members.all():
        score = models.RoomScores.objects.get(room=room, user=user)
        temp = {
            "username": user.username,
            "name": user.first_name,
            "user_id":user.id,
            "score": score.score,
            "game_over":score.game_over,
            "life":score.life,
            "game_started":room.game_started,
            "game_finished":room.match_ended,
        }
        if room.match_ended :
            temp["winner"] =  {"user_id":room.winner.id}

        res.append( temp )
        res.sort(key=lambda x: x["score"], reverse=True)
    return res

@database_sync_to_async
def addToRoom(rid, user):
    room = models.Room.objects.get(room_id=rid)
    room.members.add(user)
    res = models.RoomScores.objects.filter(room=room, user=user)
    if not res.exists():
        models.RoomScores.objects.create(room=room, user=user)
    res =  get_room_members(room)
    return res
 

@database_sync_to_async
def removeFromRoom(rid, user):
    room = models.Room.objects.get(room_id=rid)
    room.members.remove(user)
    res =  get_room_members(room)
    return res



@database_sync_to_async
def roomStartGame(rid):
    room = models.Room.objects.get(room_id=rid)
    room.game_started = True
    room.save()


@database_sync_to_async
def IncreaseScore(rid, user, new_score):
    room = models.Room.objects.get(room_id=rid)
    rs = models.RoomScores.objects.get(room=room, user=user)
    rs.score += new_score
    rs.save()
    return get_room_members(room)

# @database_sync_to_async
# def set_game_over(rid, user):
#     room = models.Room.objects.get(room_id=rid)
#     rs = models.RoomScores.objects.get(room=room, user=user)
#     e
#     rs.life = 0
#     rs.save()

#     return get_room_members(room)



@database_sync_to_async
def decrease_life(rid, user):
    room = models.Room.objects.get(room_id=rid)
    rs = models.RoomScores.objects.get(room=room, user=user)
    rs.life -= 1
    if(rs.life <= 0):
        rs.game_over = True
    rs.save()
    return get_room_members(room)





@database_sync_to_async
def search_for_winner(rid):
    room = models.Room.objects.get(room_id=rid)
    if(room.game_started):
        remaining = []

        for user in room.members.all():
            i = models.RoomScores.objects.get(room=room, user=user)
            if not i.game_over:
                remaining.append(user)

        if len(remaining) == 1:
            # remaining usera are now 1 means all players are out
            # end matche
            room.match_ended = True
            # set winner 
            room.winner = remaining[0]
            room.save()
            return get_room_members(room)
    return False



class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"].get("room_name")
        self.room_group_name = f"objhunt_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        members = await addToRoom(self.room_name, self.scope["user"])
         
        await self.channel_layer.group_send(self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}})
        print("room connect")


    async def disconnect(self, close_code):
        # Leave room group
        members = await removeFromRoom(self.room_name, self.scope["user"])

        await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}}
            )

        # await self.channel_layer.group_discard(
        #     self.room_group_name, self.channel_name
        # )

    # Receive message from WebSocket
    async def receive_json(self, text_data):



        winner = await search_for_winner(self.room_name)

        if(winner):
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"matchEnded", "data":winner}}
            )

        elif(text_data["type"] == "newJoin"):
            members = await addToRoom( self.room_name, self.scope["user"])
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}}
            )


        elif(text_data["type"] == "start"):
            # set room flag to start
            await roomStartGame(self.room_name)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"start"}}
            )
            user = self.scope["user"]
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"chatMessage", "data":{"name":user.first_name, "username":user.username, "message":f"{user.first_name} started the match."} }}
            )


        elif text_data["type"] == "chatMessage":
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"chatMessage", "data":text_data["data"] }}
            )

        elif text_data["type"] == "scoreUpdate":
            members = await IncreaseScore( self.room_name, self.scope["user"], text_data["data"]["score"])
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}}
            )

        # elif text_data["type"] == "gameOver":
        #     user = self.scope["user"]
        #     members = await set_game_over(self.room_name, user)
        #     await self.channel_layer.group_send(
        #         self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}}
        #     )

        elif text_data["type"] == "updateLife":
            user = self.scope["user"]
            members = await decrease_life(self.room_name, user)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send.json", "payload": {"type":"newJoin", "data":members}}
                )
