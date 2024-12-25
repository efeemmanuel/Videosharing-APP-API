from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTests(APITestCase):
    # Base URL for registration and token endpoints
    register_url = '/api/register/'
    token_url = '/api/token/'
    token_refresh_url = '/api/token/refresh/'

    def test_user_registration_valid_data(self):
        """
        Test that a user can register with valid data.
        """
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "securepassword123"
        }
        response = self.client.post(self.register_url, data)
        # Ensure the response status is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the username is in the response
        self.assertIn("username", response.data)
        # Verify the user is actually created in the database
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_user_registration_missing_fields(self):
        """
        Test that registration fails when required fields are missing.
        """
        data = {
            "username": "testuser",
            "email": "testuser@example.com"
            # Missing first_name, last_name, and password
        }
        response = self.client.post(self.register_url, data)
        # Ensure the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify that the user was not created
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_user_registration_invalid_email(self):
        """
        Test that registration fails with an invalid email format.
        """
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "password": "securepassword123"
        }
        response = self.client.post(self.register_url, data)
        # Ensure the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the email error is returned
        self.assertIn("email", response.data)

    def test_token_generation_valid_credentials(self):
        """
        Test that a token is generated with valid credentials.
        """
        # Create a test user
        user = User.objects.create_user(
            username="testuser",
            password="securepassword123"
        )
        data = {
            "username": "testuser",
            "password": "securepassword123"
        }
        response = self.client.post(self.token_url, data)
        # Ensure the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that access and refresh tokens are in the response
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_generation_invalid_credentials(self):
        """
        Test that token generation fails with invalid credentials.
        """
        data = {
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.token_url, data)
        # Ensure the response status is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verify that the error message is returned in the 'detail' key
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "No active account found with the given credentials")


    def test_token_refresh(self):
        """
        Test that a refresh token can be used to obtain a new access token.
        """
        # Create a test user and generate tokens
        user = User.objects.create_user(
            username="testuser",
            password="securepassword123"
        )
        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh)
        }
        response = self.client.post(self.token_refresh_url, data)
        # Ensure the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that a new access token is returned
        self.assertIn("access", response.data)





























from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from appapi.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile

class VideoTests(APITestCase):
    def setUp(self):
        """
        Set up the test environment by creating users, authenticating, 
        and creating sample video data.
        """
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword")
        
        # Create sample video
        self.video = Video.objects.create(
            video="sample.mp4",
            title="Test Video",
            desc="Test description",
            creator=self.user,
        )
        
        # Define URLs
        self.video_list_url = "/api/videos/"
        self.video_detail_url = f"/api/videos/{self.video.id}/"

        # Initialize API client
        self.client = APIClient()

    def test_video_list_authenticated(self):
        """
        Ensure all videos are returned for authenticated users.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.video_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least one video should be present

    def test_video_list_unauthenticated(self):
        """
        Test unauthorized access to the video list.
        """
        response = self.client.get(self.video_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_video_detail_authenticated(self):
        """
        Ensure a video can be retrieved by its ID for authenticated users.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.video_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.video.title)

    def test_video_detail_unauthenticated(self):
        """
        Test unauthorized access to a specific video.
        """
        response = self.client.get(self.video_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_video_delete_owner(self):
        """
        Test that only the owner or admin can delete a video.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.video_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_video_delete_non_owner(self):
        """
        Test that non-owners cannot delete a video.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.video_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_video_update(self):
        """
        Test video update functionality.
        """
        self.client.force_authenticate(user=self.user)
        updated_data = {
            "title": "Updated Title",
            "desc": "Updated Description",
        }
        response = self.client.put(self.video_detail_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], updated_data["title"])
        self.assertEqual(response.data["desc"], updated_data["desc"])

   

    def test_video_creation_authenticated(self):
        """
        Ensure authenticated users can create a video.
        """
        self.client.force_authenticate(user=self.user)
        new_video_data = {
            "video": SimpleUploadedFile("new_sample.mp4", b"file_content", content_type="video/mp4"),
            "title": "New Video",
            "desc": "New Description",
        }
        response = self.client.post(self.video_list_url, new_video_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], new_video_data["title"])


    def test_video_creation_unauthenticated(self):
        """
        Test that unauthenticated users cannot create a video.
        """
        new_video_data = {
            "video": "new_sample.mp4",
            "title": "New Video",
            "desc": "New Description",
        }
        response = self.client.post(self.video_list_url, new_video_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_video_creation_missing_fields(self):
        """
        Test validation for missing required fields during video creation.
        """
        self.client.force_authenticate(user=self.user)
        incomplete_data = {
            "title": "Incomplete Video",
            # Missing 'video' and 'desc'
        }
        response = self.client.post(self.video_list_url, incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video", response.data)
        self.assertIn("desc", response.data)





































































# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User
# from appapi.models import Post

# class PostTests(APITestCase):
#     def setUp(self):
#         """
#         Set up the test environment by creating users, authenticating, 
#         and creating sample post data.
#         """
#         # Create test users
#         self.user = User.objects.create_user(username="testuser", password="testpassword")
#         self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword")
        
#         # Authenticate the user
#         self.client.login(username="testuser", password="testpassword")
        
#         # Create sample post
#         self.post = Post.objects.create(
#             title="Test Post",
#             content="Test post content",
#             creator=self.user,
#         )
        
#         # Define URLs
#         self.post_list_url = "/api/posts/"
#         self.post_detail_url = f"/api/posts/{self.post.id}/"

#     # Post List Tests
#     def test_post_list_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.post_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertGreaterEqual(len(response.data), 1)

#     def test_post_list_unauthenticated(self):
#         self.client.logout()
#         response = self.client.get(self.post_list_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Post Detail Tests
#     def test_post_detail_authenticated(self):
#         response = self.client.get(self.post_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["title"], self.post.title)

#     def test_post_detail_unauthenticated(self):
#         self.client.logout()
#         response = self.client.get(self.post_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Post Update & Delete Tests
#     def test_post_delete_owner(self):
#         response = self.client.delete(self.post_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_post_delete_non_owner(self):
#         self.client.logout()
#         self.client.login(username="adminuser", password="adminpassword")
#         response = self.client.delete(self.post_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_post_update(self):
#         updated_data = {
#             "title": "Updated Post Title",
#             "content": "Updated post content",
#         }
#         response = self.client.put(self.post_detail_url, updated_data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["title"], updated_data["title"])
#         self.assertEqual(response.data["content"], updated_data["content"])

#     # Post Creation Tests
#     def test_post_creation_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         new_post_data = {
#             "title": "New Post",
#             "content": "This is a new post.",
#         }
#         response = self.client.post(self.post_list_url, new_post_data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["title"], new_post_data["title"])

#     def test_post_creation_missing_fields(self):
#         incomplete_data = {
#             "title": "Incomplete Post",
#             # Missing 'content'
#         }
#         response = self.client.post(self.post_list_url, incomplete_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("content", response.data)






































































# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User
# from appapi.models import Comment, Post

# class CommentTests(APITestCase):
#     def setUp(self):
#         """
#         Set up the test environment by creating users, authenticating, 
#         and creating sample comment data.
#         """
#         # Create test users
#         self.user = User.objects.create_user(username="testuser", password="testpassword")
#         self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword")
        
#         # Authenticate the user
#         self.client.login(username="testuser", password="testpassword")
        
#         # Create sample post and comment
#         self.post = Post.objects.create(
#             title="Test Post",
#             content="Test post content",
#             creator=self.user,
#         )
#         self.comment = Comment.objects.create(
#             content="Test comment",
#             post=self.post,
#             creator=self.user,
#         )
        
#         # Define URLs
#         self.comment_list_url = f"/api/posts/{self.post.id}/comments/"
#         self.comment_detail_url = f"/api/comments/{self.comment.id}/"

#     # Comment List Tests
#     def test_comment_list_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.comment_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertGreaterEqual(len(response.data), 1)

#     def test_comment_list_unauthenticated(self):
#         self.client.logout()
#         response = self.client.get(self.comment_list_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Comment Detail Tests
#     def test_comment_detail_authenticated(self):
#         response = self.client.get(self.comment_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["content"], self.comment.content)

#     def test_comment_detail_unauthenticated(self):
#         self.client.logout()
#         response = self.client.get(self.comment_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Comment Deletion Tests
#     def test_comment_delete(self):
#         response = self.client.delete(self.comment_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     # Comment Creation Tests
#     def test_comment_creation_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         new_comment_data = {
#             "content": "This is a new comment.",
#         }
#         response = self.client.post(self.comment_list_url, new_comment_data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["content"], new_comment_data["content"])

#     def test_comment_creation_missing_fields(self):
#         incomplete_data = {
#             # Missing 'content'
#         }
#         response = self.client.post(self.comment_list_url, incomplete_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("content", response.data)






































































# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User
# from appapi.models import Subscription

# class SubscriptionTests(APITestCase):
#     def setUp(self):
#         """
#         Set up the test environment by creating users, authenticating, 
#         and creating sample subscription data.
#         """
#         # Create test users
#         self.user = User.objects.create_user(username="testuser", password="testpassword")
#         self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")
#         self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword")
        
#         # Authenticate the user
#         self.client.login(username="testuser", password="testpassword")
        
#         # Define URLs
#         self.subscription_list_url = "/api/subscriptions/"
#         self.subscription_detail_url = f"/api/subscriptions/{self.user.id}/"

#     # Subscription List Tests
#     def test_subscription_list_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.subscription_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertGreaterEqual(len(response.data), 1)

#     def test_subscription_list_unauthenticated(self):
#         self.client.logout()
#         response = self.client.get(self.subscription_list_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Subscription Detail Tests
#     def test_subscription_delete_owner(self):
#         response = self.client.delete(self.subscription_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_subscription_delete_unauthorized(self):
#         self.client.logout()
#         self.client.login(username="adminuser", password="adminpassword")
#         response = self.client.delete(self.subscription_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     # Subscription Creation Tests
#     def test_subscription_creation(self):
#         self.client.force_authenticate(user=self.user)
#         subscription_data = {
#             "subscribed_to": self.other_user.id,
#         }
#         response = self.client.post(self.subscription_list_url, subscription_data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_subscription_creation_self_subscription(self):
#         self.client.force_authenticate(user=self.user)
#         subscription_data = {
#             "subscribed_to": self.user.id,  # User is subscribing to themselves
#         }
#         response = self.client.post(self.subscription_list_url, subscription_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("detail", response.data)

#     def test_subscription_creation_duplicate(self):
#         self.client.force_authenticate(user=self.user)
#         subscription_data = {
#             "subscribed_to": self.other_user.id,
#         }
#         # Subscribe the user
#         self.client.post(self.subscription_list_url, subscription_data)
#         # Try subscribing again
#         response = self.client.post(self.subscription_list_url, subscription_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("detail", response.data)
