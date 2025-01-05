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





























# from rest_framework.test import APITestCase, APIClient
# from rest_framework import status
# from django.contrib.auth.models import User
# from appapi.models import Video
# from django.core.files.uploadedfile import SimpleUploadedFile

# class VideoTests(APITestCase):
#     def setUp(self):
#         """
#         Set up the test environment by creating users, authenticating, 
#         and creating sample video data.
#         """
#         # Create test users
#         self.user = User.objects.create_user(username="testuser", password="testpassword")
#         self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword")
        
#         # Create sample video
#         self.video = Video.objects.create(
#             video="sample.mp4",
#             title="Test Video",
#             desc="Test description",
#             creator=self.user,
#         )
        
#         # Define URLs
#         self.video_list_url = "/api/videos/"
#         self.video_detail_url = f"/api/videos/{self.video.id}/"

#         # Initialize API client
#         self.client = APIClient()

#     def test_video_list_authenticated(self):
#         """
#         Ensure all videos are returned for authenticated users.
#         """
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.video_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertGreaterEqual(len(response.data), 1)  # At least one video should be present

#     def test_video_list_unauthenticated(self):
#         """
#         Test unauthorized access to the video list.
#         """
#         response = self.client.get(self.video_list_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_video_detail_authenticated(self):
#         """
#         Ensure a video can be retrieved by its ID for authenticated users.
#         """
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.video_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["title"], self.video.title)

#     def test_video_detail_unauthenticated(self):
#         """
#         Test unauthorized access to a specific video.
#         """
#         response = self.client.get(self.video_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_video_delete_owner(self):
#         """
#         Test that only the owner or admin can delete a video.
#         """
#         self.client.force_authenticate(user=self.user)
#         response = self.client.delete(self.video_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_video_delete_non_owner(self):
#         """
#         Test that non-owners cannot delete a video.
#         """
#         self.client.force_authenticate(user=self.admin_user)
#         response = self.client.delete(self.video_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_video_update(self):
#         """
#         Test video update functionality.
#         """
#         self.client.force_authenticate(user=self.user)
#         updated_data = {
#             "title": "Updated Title",
#             "desc": "Updated Description",
#         }
#         response = self.client.put(self.video_detail_url, updated_data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["title"], updated_data["title"])
#         self.assertEqual(response.data["desc"], updated_data["desc"])

   

#     def test_video_creation_authenticated(self):
#         """
#         Ensure authenticated users can create a video.
#         """
#         self.client.force_authenticate(user=self.user)
#         new_video_data = {
#             "video": SimpleUploadedFile("new_sample.mp4", b"file_content", content_type="video/mp4"),
#             "title": "New Video",
#             "desc": "New Description",
#         }
#         response = self.client.post(self.video_list_url, new_video_data, format="multipart")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["title"], new_video_data["title"])


#     def test_video_creation_unauthenticated(self):
#         """
#         Test that unauthenticated users cannot create a video.
#         """
#         new_video_data = {
#             "video": "new_sample.mp4",
#             "title": "New Video",
#             "desc": "New Description",
#         }
#         response = self.client.post(self.video_list_url, new_video_data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_video_creation_missing_fields(self):
#         """
#         Test validation for missing required fields during video creation.
#         """
#         self.client.force_authenticate(user=self.user)
#         incomplete_data = {
#             "title": "Incomplete Video",
#             # Missing 'video' and 'desc'
#         }
#         response = self.client.post(self.video_list_url, incomplete_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("video", response.data)
#         self.assertIn("desc", response.data)












