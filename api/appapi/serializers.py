from rest_framework import serializers
from .models import Video, Post, Comment, Subscription 
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password']
    
    def create(self, validated_data):
        user = User.objects.create(
        email=validated_data['email'],
        username=validated_data['username'],
        password = make_password(validated_data['password'])
        )
        user.set_password(validated_data['password'])
        user.save()
        return user




class VideoSerilaizer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    creator = serializers.StringRelatedField()
    comments = serializers.HyperlinkedRelatedField(view_name='appapi:comments-detail',many=True,read_only=True)

    class Meta:
        model = Video
        fields = ['id','video','title','desc','comments','creator','created_at']
        read_only_fields = ['id','creator']

    def update(self, instance, validated_data):
        instance.created_at = timezone.now()
        return super().update(instance, validated_data)
    
    
    
    
class UpdateVideoSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = Video
        fields = ['id','video','title','desc', 'creator','created_at']
        read_only_fields = ['id', 'video', 'creator','created_at']










class PostSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['id','post', 'post_image','creator']
        read_only_fields = ['id','creator']
    
    








class CommentSerializer(serializers.ModelSerializer):
    # the_video = serializers.HyperlinkedRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = Comment
        fields = ['comment','the_video']
        







class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription 
        fields = ['id','subscriber','subscribed_to']
        read_only_fields = ['id','subscriber']

    def validate(self, data):
        # Access the logged-in user from the request context
        subscriber = self.context['request'].user
        subscribed_to = data.get("subscribed_to")

        if subscriber == subscribed_to:
            raise serializers.ValidationError("cannot subscribe to yourself")
    
        
        return data
    




# When to Use self.context:
# Use it when you need data (like the request or user) that is not part of the serialized input but is available in the view.
# It’s especially useful when dealing with read-only fields or fields that are automatically set, like subscriber in your case.
