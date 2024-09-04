from UserApp.models import UserData
from rest_framework import serializers
class UserDataSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = UserData
        # fields = '__all__'
        fields = ['id','name','email','contact','address','password'] #excepting password we are sending all data

    def validate(self, data):
        # Check if email is already in use
        email = data.get('email')
        if UserData.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return data
    def create(self, validated_data):
            # Remove the password from validated_data
            password = validated_data.pop('password')
            # Create the user without setting the password initially
            user = UserData(**validated_data)
            # Use set_password to hash the password
            user.set_password(password)
            user.save()
            return user

    def update(self, instance, validated_data):
        # Handle updating the password securely
            password = validated_data.pop('password', None)  # Pop the password if present
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            if password:
                instance.set_password(password)
            instance.save()
            return instance