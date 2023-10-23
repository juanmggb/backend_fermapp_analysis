from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .serializers import UserSerializer, MemberSerializer
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import AnonymousUser


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # This will put data INSIDE the token
    # @classmethod
    # def get_token(cls, user):

    #     token = super().get_token(user)

    #     # Add custom claims
    #     token['id'] = user.id
    #     token['username'] = user.username
    #     token['first_name'] = user.first_name
    #     token['last_name'] = user.last_name
    #     token['email'] = user.email
    #     token['is_staff'] = user.is_staff
    #     # token['image'] = user.member.image

    #     return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra response here
        data.update(
            {
                "user_id": self.user.id,
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "is_staff": self.user.is_staff,
                # THIS IS THE ERROR
                "image": self.user.member.image.url
                if self.user.member and self.user.member.image
                else None,
            }
        )

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Create your views here.


@api_view(["GET"])
def user_list(request):
    queryset = User.objects.all()

    serializer = UserSerializer(queryset, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def register_user(request):
    data = request.data.copy()

    data["password"] = make_password(data["password"])

    if data.get("role") == "Lab Director":
        data.update(is_staff=True)

    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user_instance = serializer.save()

        data.update(user=user_instance.id)

        member_serializer = MemberSerializer(data=data)
        if member_serializer.is_valid():
            member_serializer.save()
        else:
            print(member_serializer.errors)
            return Response(
                member_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_user(request):
    user = request.user

    if isinstance(user, AnonymousUser):
        return Response(
            {"error": "You must be authenticated to modify your account"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    data = request.data
    print("DATA", data)

    username = data.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    image = data.get("image[]")
    # image = request.FILES.get('image')

    # try:
    user.username = username
    user.first_name = first_name
    user.last_name = last_name

    if email:
        user.email = email

    if image:
        member = user.member
        member.image = image
        print("MEMBER", member)
        member.save()

    # Check if current_password was provided and matches the user's password
    if current_password and check_password(current_password, user.password):
        # If it matches, set the new password
        user.password = make_password(new_password)
    elif current_password:
        # If it doesn't match, return an error
        return Response(
            {"error": "Current password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)
    # except:
    #     return Response({'error': 'Error when updating user'}, status=status.HTTP_400_BAD_REQUEST)
