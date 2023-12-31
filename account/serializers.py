from rest_framework import serializers
from django.contrib.auth import get_user_model
from course_impressions.serializers import FavoriteSerializer
from rest_framework.response import Response

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=20, required=True, write_only=True)
    password_confirmation = serializers.CharField(min_length=6, max_length=20, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation',
                  'balance', 'first_name', 'last_name', 'avatar')

    def validate(self, attrs):
        password = attrs['password']
        password_confirmation = attrs.pop('password_confirmation')

        if password != password_confirmation:
            raise serializers.ValidationError('Passwords do not match')

        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError('Password must contain letters and numbers')

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['favorites'] = FavoriteSerializer(instance.favorites.all(), many=True, required=False).data
        return data


class ActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        self.activation_code = attrs['activation_code']
        return attrs

    def save(self, **kwargs):
        try:
            user = User.objects.get(activation_code=self.activation_code)
            user.is_active = True
            user.activation_code = ''
            user.balance += 500
            user.save()
        except:
            self.fail('Incorrect activation code')


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, max_length=20, required=True, write_only=True)
    password_confirmation = serializers.CharField(min_length=6, max_length=20, required=True, write_only=True)

    def validate(self, attrs):
        password = attrs['new_password']
        password_confirmation = attrs.pop('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError(
                'Passwords must be the same'
            )
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError(
                'The password must contain letters and numbers'
            )
        return attrs


class GetActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(decimal_places=2, max_digits=9)

    def validate(self, attrs):
        user = self.context['user']
        if not User.objects.filter(email=user.email).exists():
            return Response('Current user doesnt exist', status=400)
        return attrs


class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(decimal_places=2, max_digits=9)
    order = serializers.IntegerField(required=True)

    def validate(self, attrs):
        order_id = attrs['order']
