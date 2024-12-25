from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Video(models.Model):
    video = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=40)
    desc = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"title: {self.title}, created at: {self.created_at}"
    
    
class Post(models.Model):
    post = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    post_image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    def __str__(self):
        return self.post
    

class Comment(models.Model):
    comment = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    the_video = models.ForeignKey(Video, related_name='comments',on_delete=models.CASCADE)

    def __str__(self):
        return self.comment
    

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriber',on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"subscriber: {self.subscriber} - subscribed_to: {self.subscribed_to} "
    
    

    
