from rest_framework import serializers

from django.contrib.auth.models import User
from .models import Member


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    password = serializers.CharField(write_only=True)

    def get_member(self, obj):
        try:
            return MemberSerializer(obj.member).data
        except Member.DoesNotExist:
            return None

    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'member', 'username', 'first_name',
                  'last_name', 'email', 'is_staff', 'password')
