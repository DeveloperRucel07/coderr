from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from auth_app.models import Profile


class LoginWithEmailSerializer(serializers.ModelSerializer):
    '''
    Login Serializer.
    read all login informations
    validate if the information are corresponding to the pretent user or not.
    
    '''
    username = serializers.CharField()
    password = serializers.CharField(write_only= True)
    
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
    
    def validate(self, data):
        '''
        Validate the login data by checking username and password.

        Args:
            data (dict): The data to validate containing username and password.

        Returns:
            dict: The validated data with user added.

        Raises:
            ValidationError: If username or password is invalid.
        '''
        username = data.get('username')
        password = data.get('password')  
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')

        user = authenticate(username= username, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid email or password')

        data['user'] = user
        return data

class RegistrationSerializer(serializers.ModelSerializer):
    '''
    Registration Serializer.
    read all registration informations
    write the fullname by assigning it to the username
    validate if the both password are correct or not.
    
    '''
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices = Profile.USER_TYPES)
    class Meta:
        model = User
        fields = ['username', 'email','password', 'repeated_password','type']
        extra_kwargs = {
            'password':{
                'write_only': True
            }
        }
        
    def save(self):
        ''' if all required informations was correct, create a user.

        Raises:
            serializers.ValidationError: password don't match
            serializers.ValidationError: the email already exists

        Returns:
            user data: a user information
        '''
        
        
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error':'passwords dont match'})
        
        if User.objects.filter(email = self.validated_data['email']).exists():
            raise serializers.ValidationError({'error':'this Email already exists'})
        
        account = User(email = self.validated_data['email'], username = self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    file = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'email',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'created_at',
        ]
        
    def get_file(self, obj):
        return obj.file.url if obj.file else '' 
        
class ProfileCustomerSerialiser(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    file = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['user','username', 'first_name', 'last_name', 'file', 'type' ]  
        
    def get_file(self, obj):
        return obj.file.url if obj.file else '' 
    
class ProfileBusinessSerialiser(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    file = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['user','username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type' ] 
    
    def get_file(self, obj):
        return obj.file.url if obj.file else ''