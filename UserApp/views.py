from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from jsonschema import validate, ValidationError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from .models import UserData
from UserApp.serializers import UserDataSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination

create_user_input_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "contact": {"type": "string"},
        "address": {"type": "string"}
    },
    "required": ["name", "email", "password", "contact"]
}

list_user_response_schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "contact": {"type": "string"},
                    "address": {"type": "string"}
                },
                "required": ["id", "name", "email", "contact"]
            }
        }
    },
    "required": ["users"]
}

login_user_input_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"]
}
#code for pegination concpts in django
from rest_framework.pagination import PageNumberPagination

class UserDataPagination(PageNumberPagination):
    page_size = 3  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

@csrf_exempt
@api_view(['POST'])
def createUser(request):
    try:
        if request.method == 'POST':
            try: 
                validate(instance=request.data, schema=create_user_input_schema)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        
            serializer = UserDataSerializer(data=request.data)
            print(serializer)
            if serializer.is_valid():
                user_obj = serializer.save()
                sum = 4/0
                return Response ({"message":"success","id":user_obj.id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def listUser(request):
    if request.method == 'GET':
        user_obj = UserData.objects.all().order_by('id')
        
        #pegination code for django
        paginator = UserDataPagination()

        paginated_users = paginator.paginate_queryset(user_obj, request)

        serializer = UserDataSerializer(paginated_users, many=True) #chaged user_obj to paginated_users
        data = serializer.data
        # data ={"name":"rajashri","email":"raj@chatrikar@gmail.com","contact":"1234567890","address":"pune"}

        try:
            validate(instance={"users": data}, schema=list_user_response_schema)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data, status=status.HTTP_200_OK)
    return HttpResponse("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST','GET'])
def loginUser(request):

    if request.method == 'POST':
        if not 'email' in request.data or not 'password' in request.data:
            return Response({"message":"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate(instance=request.data, schema=login_user_input_schema)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        email = request.data.get('email')
        password = request.data.get('password')
        

        user_obj = UserData.objects.filter(email=email, password=password)
        if user_obj:
            refresh = RefreshToken.for_user(user_obj[0])
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            serializer = UserDataSerializer(user_obj[0])
            return Response({"message":"login Successfully!!","logged user":serializer.data.get('id'),"access": access_token,
                "refresh": refresh_token}, status=status.HTTP_200_OK)
        return Response({"message":"Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
    return HttpResponse("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        print("HELLO")
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return Response({"message":"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        print(auth_header)
             # Extract the token from the Authorization header
        token_str = auth_header.split(' ')[1]
        token = AccessToken(token_str)

        # Access the claims in the JWT token
        claims = token.payload
        print("Claims:", claims['user_id'])

        #get the data of employee with id from claims
        user_obj = UserData.objects.get(id=claims['user_id'])
        serializer = UserDataSerializer(user_obj)  #conveterd the query set to json

        return Response({
            "message": f"Profile fetched successfully for user{claims['user_id']}","data":serializer.data
        }, status=status.HTTP_200_OK)     
        
       
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# @csrf_exempt
@api_view(['PUT','GET'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user = request.user  # Get the logged-in user

        if request.method == 'GET':
            # Fetch the profile data of the logged-in user
            serializer = UserDataSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            # Update the user's profile data
            serializer = UserDataSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Profile Updated Successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout Successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)