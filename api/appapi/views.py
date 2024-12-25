from django.shortcuts import render
from .models import Video, Post, Comment, Subscription
from .serializers import VideoSerilaizer, UpdateVideoSerializer, PostSerializer,CommentSerializer, UserSerializer, SubscriptionSerializer


from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import exception_handler


from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from .permissions import *

# Create your views here.



class Register(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        





class VideoList(APIView):
  
    serializer_class = VideoSerilaizer
    parser_classes = (MultiPartParser, FormParser)

    permission_classes = [IsAuthenticated]

    def get(self, request,*args, **kwargs):
        videos = Video.objects.all()
        serializer = self.serializer_class(videos, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





class VideoDetail(APIView):

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        
    def get_object(self, pk):
        try:
            obj = Video.objects.get(pk=pk)
            # Check object-level permissions
            self.check_object_permissions(self.request, obj)
            return obj
        except Video.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        video = self.get_object(pk)
        serializer = VideoSerilaizer(video, context={'request': request})
        return Response(serializer.data)
    

    def delete(self, request, pk):
        videos = self.get_object(pk)
        videos.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
   
    def put(self, request, pk):
        videos = self.get_object(pk)
        serializer = UpdateVideoSerializer(videos,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# request.data is basically data sent in the request body from the client.





class PostList(APIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        queryset = Post.objects.all()
        serializer = self.serializer_class(queryset,many=True)
        return Response (serializer.data)
    
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Set the creator to the logged-in user before saving
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class PostDetail(APIView):


    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    

        
    def get_object(self, pk):
        try:
            obj = Post.objects.get(pk=pk)
            # Check object-level permissions
            self.check_object_permissions(self.request, obj)
            return obj
        except Post.DoesNotExist:
            raise Http404



    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = PostSerializer(queryset)
        return Response (serializer.data)
    

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = PostSerializer(queryset, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def delete(self, request, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response (status=status.HTTP_204_NO_CONTENT)
    
    





class CommentList(APIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class =  CommentSerializer


    def get(self, request,*args, **kwargs):
        queryset = Comment.objects.all()
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CommentDetail(APIView):
    def get_object(self,pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404
    

    def get(self, request, pk,*args, **kwargs):
        queryset = self.get_object(pk)
        serializer = CommentSerializer(queryset,context={'request': request})
        return Response(serializer.data)
    

    def delete(self, request, pk):
        queryset = self.get_object(pk)
        queryset.delete()





    

    
class SubscriptionList(APIView):
    
    serializer_class = SubscriptionSerializer


    def get(self, request):
        queryset = Subscription.objects.filter(subscriber=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(subscriber=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SubscriptionDetail(APIView):
    def get_object(self,pk):
        try:
            return Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            raise Http404  


    # def delete(self, request, pk):
    #     queryset = self.get_object(pk)
    #     queryset.delete()
    
    def delete(self, request, pk):
        subscription = self.get_object(pk)
        if subscription.subscriber != request.user:
            return Response({"detail": "You cannot delete someone else's subscription."}, status=status.HTTP_403_FORBIDDEN)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
          





    