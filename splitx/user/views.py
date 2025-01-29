from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializer import SettlementSerializer, UserSerializer,TransactionSerializer
from rest_framework import permissions
from .models import Group, Settlement, Transaction, User
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
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

@api_view(['POST'])
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
        print("error ocuccered at signup",str(e))
        return JsonResponse({'error': 'Something Went Wrong', 'details': str(e)}, status=400)

@api_view(['POST'])
def refresh(request):
    try:
        refresh = request.data.get('refresh')
        token = RefreshToken(refresh)
        return JsonResponse({'access': str(token.access_token)})
    except Exception as e:
        print("error ocuccered at refresh",str(e))
        return JsonResponse({'error': 'Invalid Token', 'details': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
        print("error ocuccered at user",str(e))
        return JsonResponse({'error': 'Something Went Wrong', 'details': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense(request):
        try:
            user = request.user 
            print(user)
            transactions = Transaction.objects.filter(user__email=user)
            print(transactions)
            transaction_serializer = TransactionSerializer(transactions, many=True)
            return JsonResponse(transaction_serializer.data, safe=False, status=200)
        except Exception as e:
            print("error ocuccered at expense",str(e))
            return JsonResponse({ "error":"Something Went Wrong","details":str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        print("error ocuccered at create_expense",str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        print("error ocuccered at expense_split",str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settlement(request):
    try:
        user = request.user
        settlements = Settlement.objects.filter(user_to_pay__email=user)
        settlement_serializer = SettlementSerializer(settlements, many=True)
        return JsonResponse(settlement_serializer.data, safe=False, status=200)
    except Exception as e:
        print("error ocuccered at settlement",str(e))
        return JsonResponse("Something Went Wrong", status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_monthly(request):
    try:
        user = request.user
        transactions = Transaction.objects.filter(user__email=user)
        total = 0
        category_totals = {}
        for transaction in transactions:
            total += transaction.amount
            category = transaction.category
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += transaction.amount
        return JsonResponse({'total': total, 'category_totals': category_totals}, status=200)
    except Exception as e:
        print("error ocuccered at stats_monthly", str(e))
        return JsonResponse("Something Went Wrong", status=400)
    

