app_name = "appapi
from .views import *

from django.urls import path, include



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # videos endpoint
    path('api/videos/', VideoList.as_view(), name='videos-detail'),
    path('api/videos/<int:pk>/', VideoDetail.as_view(), name='videos-detail'),

  

    # post endpoint
    path('api/posts/', PostList.as_view()),
    path('api/posts/<int:pk>/', PostDetail.as_view()),

    # comment endpoint
    path('api/comments/', CommentList.as_view(), name='comments-detail'),
    path('api/comments/<int:pk>/', CommentDetail.as_view(), name='comments-detail'),

    # subscription endpoint
    path('api/subscriptions/', SubscriptionList.as_view(), name='subscriptions-detail'),
    path('api/subscriptions/<int:pk>/', SubscriptionDetail.as_view()),



    # Authentication
    path('api/register/', Register.as_view()),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
