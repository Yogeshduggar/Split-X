import os
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializer import GroupSerializer, SettlementSerializer, UserSerializer, TransactionSerializer
from rest_framework import permissions
from .models import Group, Settlement, Transaction, User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from openai.main import extract_total_bill_amount
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password'],
    ),
    responses={200: 'Success', 400: 'Invalid credentials'}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([UserRateThrottle])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    print(username, password)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password', 'email', 'first_name', 'last_name'],
    ),
    responses={201: 'Created', 400: 'Error'}
)
@api_view(['POST'])
@throttle_classes([UserRateThrottle])
def signup(request):
    try:
        User = get_user_model()
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, status=201)
    except Exception as e:
        print("error ocuccered at signup", str(e))
        return JsonResponse({'error': 'Something Went Wrong', 'details': str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['refresh'],
    ),
    responses={200: 'Success', 400: 'Invalid Token'}
)
@api_view(['POST'])
@throttle_classes([UserRateThrottle])
def refresh(request):
    try:
        refresh = request.data.get('refresh')
        token = RefreshToken(refresh)
        return JsonResponse({'access': str(token.access_token)})
    except Exception as e:
        print("error ocuccered at refresh", str(e))
        return JsonResponse({'error': 'Invalid Token', 'details': str(e)}, status=400)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('user', openapi.IN_QUERY, type=openapi.TYPE_STRING)
    ],
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def user(request):
    try:
        user = request.query_params.get('user')
        if user is None:
            user_obj = User.objects.all()
            user_serializer = UserSerializer(user_obj, many=True)
        else:
            user_obj = User.objects.get(email=user)
            user_serializer = UserSerializer(user_obj)
        return JsonResponse(user_serializer.data, status=200)
    except Exception as e:
        print("error ocuccered at user", str(e))
        return JsonResponse({'error': 'Something Went Wrong', 'details': str(e)}, status=400)

@swagger_auto_schema(
    method='get',
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def expense(request):
    try:
        user = request.user 
        print(user)
        transactions = Transaction.objects.filter(user__email=user)
        transaction_serializer = TransactionSerializer(transactions, many=True)
        return JsonResponse(transaction_serializer.data, safe=False, status=200)
    except Exception as e:
        print("error ocuccered at expense", str(e))
        return JsonResponse({ "error":"Something Went Wrong","details":str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    request_body=TransactionSerializer,
    responses={201: 'Created', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def create_expense(request):
    try:
        user = request.user
        data = request.data
        data['user'] = user.id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        print("error ocuccered at create_expense", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'users_to_pay': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
            'group': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['users_to_pay', 'amount', 'group'],
    ),
    responses={201: 'Created', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def expense_split(request):
    try:
        user = request.user
        data = request.data
        users_to_pay = data.get('users_to_pay')
        amount = data.get('amount')
        group = data.get('group')
        group_obj = Group.objects.get(id=group)
        user_to_be_paid = request.user
        res = []
        amount = amount/len(users_to_pay)
        for user in users_to_pay:
            if user == user_to_be_paid:
                continue
            user_to_be_paid = User.objects.get(id=user)
            settlement = Settlement.objects.create(
                group=group_obj,
                user_to_pay=user,
                user_to_be_paid=user_to_be_paid,
                amount=amount
            )
            settlement.save()
            res.append(settlement)
        settlement_serializer = SettlementSerializer(res, many=True)
        return JsonResponse(settlement_serializer.data, status=201)
    except Exception as e:
        print("error ocuccered at expense_split", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='get',
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def settlement(request):
    try:
        user = request.user
        settlements = Settlement.objects.filter(user_to_pay__email=user)
        settlement_serializer = SettlementSerializer(settlements, many=True)
        return JsonResponse(settlement_serializer.data, safe=False, status=200)
    except Exception as e:
        print("error ocuccered at settlement", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='get',
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def stats_monthly(request):
    try:
        user = request.user
        transactions = Transaction.objects.filter(user__email=user)
        total = 0
        category_totals = {}
        for transaction in transactions:
            if transaction.type == 'Debit':
                total -= transaction.amount
            else:
                total += transaction.amount
            category = transaction.category
            if category not in category_totals:
                category_totals[category] = 0

            if transaction.type == 'Debit':
                category_totals[category] -= transaction.amount
            else:
                category_totals[category] += transaction.amount
        return JsonResponse({'total': total, 'category_totals': category_totals}, status=200)
    except Exception as e:
        print("error ocuccered at stats_monthly", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='get',
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def group(request):
    try:
        user = request.user
        groups = Group.objects.filter(users__email=user)
        group_serializer = GroupSerializer(groups, many=True)
        return JsonResponse(group_serializer.data, safe=False, status=200)
    except Exception as e:
        print("error ocuccered at group", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='post',
    request_body=GroupSerializer,
    responses={201: 'Created', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def create_group(request):
    try:
        user = request.user
        data = request.data
        admin_user_Obj = User.objects.get(email=user) 
        data['user_admin'] = [admin_user_Obj]
        user_Obj = User.objects.filter(email__in=user)
        data['users'] = [user_Obj]
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        print("error ocuccered at create_group", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'users': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
            'user_admin': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        },
        required=['id'],
    ),
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def update_group(request):
    try:
        user = request.user
        data = request.data
        group = Group.objects.get(id=data.get('id'))
        if user not in group.user_admin.all():
            return JsonResponse("You are not authorized to update this group", status=400)
        if data.get('name'):
            group.name = data.get('name')
        if data.get('description'):
            group.description = data.get('description')
        if data.get('users'):
            users = User.objects.filter(email__in=data.get('users'))
            group.users.set(users)
        if data.get('user_admin'):
            user_admin = User.objects.filter(email__in(data.get('user_admin')))
            group.user_admin.set(user_admin)
        group.save()
        group_serializer = GroupSerializer(group)
        return JsonResponse(group_serializer, status=200)
    except Exception as e:
        print("error ocuccered at update_group", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'payment_done': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        },
        required=['id'],
    ),
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def settle(request):
    try:
        user = request.user
        data = request.data
        settlement = Settlement.objects.get(id=data.get('id'))
        if data.get('payment_done'):
            settlement.status = 'Settled'
            settlement.save()
            Transaction.objects.create({
                'user': settlement.user_to_be_paid,
                'type': 'Credit',
                'category': 'Settlement',
                'amount': settlement.amount
            })
        else:
            amount = settlement.amount
            upi_id = os.getenv('UPI_ID')
            upi_name = os.getenv('UPI_NAME')
            link = f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount}&cu=INR"
            return JsonResponse({'link': link}, status=200)
    except Exception as e:
        print("error ocuccered at settle", str(e))
        return JsonResponse("Something Went Wrong", status=400)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
            'group': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['image'],
    ),
    responses={200: 'Success', 400: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def smart_bill(request):
    try:
        image = request.data.get('image')
        amount = extract_total_bill_amount(image)
        a_user = User.objects.get(email = request.user)
        try:
            amount = int(amount)
            transaction=Transaction.objects.create(
                user=a_user,
                type='Debit',
                category='Shopping',
                amount=amount
            )
            if request.data.get('group'):
                group = Group.objects.get(id= request.data.get('group'))
                users = group.users.all()
                amount = amount/len(users)
                for user in users:
                    if user != a_user:
                        settlement = Settlement.objects.create(
                            group=group,
                            user_to_pay=user,
                            user_to_be_paid=a_user,
                            amount=amount
                        )
                        settlement.save()
        except Exception as e:
            print("error ocuccered at smart_bill-1", str(e))
            return JsonResponse("Something Went Wrong", status=400)

        return JsonResponse("Sucess", status=200)
    except Exception as e:
        print("error ocuccered at smart_bill-2", str(e))
        return JsonResponse("Something Went Wrong", status=400)