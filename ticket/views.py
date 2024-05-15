from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Ticket, Wallet
from .serializers import UserSerializer, TicketSerializer
from django.contrib.auth import authenticate
from django.db import transaction


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        username = user.username
        user_det = Users.objects.get(username=username)
        user_id = user_det.user_id
        print(user_id)
        wallet = Wallet(user_id=user_det)
        try:
            wallet.save()
            print("Wallet saved successfully")
        except Exception as e:
            print("Error saving wallet:", e)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    print(email)
    print(password)


    user = Users.objects.filter(email=email, password=password)

    print(user)

    if user:
        # User is authenticated, return success response
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        # Authentication failed, return error response
        return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)




@api_view(['POST'])
def book_ticket(request):
    user_id = request.data.get('user_id')
    trip_type = request.data.get('trip_type')
    from_loc = request.data.get('from_loc')
    to_loc = request.data.get('to_loc')
    transport_date = request.data.get('transport_date')
    number_of_tickets = request.data.get('number_of_tickets')
    price = request.data.get('price')

    if None in [user_id, trip_type, from_loc, to_loc, transport_date, number_of_tickets, price]:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if trip_type == 'one_way':
        with transaction.atomic():
            try:
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)
                if wallet.wallet_balance < price:
                    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

                wallet.wallet_balance -= price
                wallet.save()

                ticket = Ticket.objects.create(
                    user_id=user, 
                    trip_type=trip_type, 
                    from_loc=from_loc, 
                    to_loc=to_loc, 
                    transport_date=transport_date, 
                    number_of_tickets=number_of_tickets, 
                    price=price
                )

                booked_ticket = {
                    "user_id": user_id,
                    "trip_type": trip_type,
                    "from_loc": from_loc,
                    "to_loc": to_loc,
                    "transport_date": transport_date,
                    "number_of_tickets": number_of_tickets,
                    "price":price
                }

                return Response(booked_ticket, status=status.HTTP_200_OK)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif trip_type == 'round_trip':
        return_date = request.data.get('return_date')
        if return_date is None:
            return Response({'error': 'Return date is required for round trip'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            try:
                price = price - (price * 0.15)
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)
                if wallet.wallet_balance < price:
                    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

                wallet.wallet_balance = float(wallet.wallet_balance) - price
                wallet.save()

                ticket = Ticket.objects.create(
                    user_id=user, 
                    trip_type=trip_type, 
                    from_loc=from_loc, 
                    to_loc=to_loc, 
                    transport_date=transport_date, 
                    return_date=return_date, 
                    number_of_tickets=number_of_tickets, 
                    price=price
                )

                booked_ticket = {
                    "user_id": user_id,
                    "trip_type": trip_type,
                    "from_loc": from_loc,
                    "to_loc": to_loc,
                    "transport_date": transport_date,
                    "return_date": return_date,
                    "number_of_tickets": number_of_tickets,
                    "price":price
                }
                return Response(booked_ticket, status=status.HTTP_200_OK)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Invalid trip type'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def history(request):
    user_id = request.data.get('user_id')

    user_tickets = Ticket.objects.filter(user_id=user_id)
    serializer = TicketSerializer(user_tickets, many=True)  # Serialize the queryset

    return Response({'user_tickets': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_ticket_price(request):
    from_loc = request.data.get('from_loc')
    to_loc = request.data.get('to_loc')

    prices = {
        ("mushin", "costain"): 100,
        ("mushin", "ilupeju"): 150,
        ("mushin", "oshodi"): 200,
        ("mushin", "yaba"): 250,
        ("costain", "mushin"): 100,
        ("costain", "ilupeju"): 150,
        ("costain", "oshodi"): 200,
        ("costain", "yaba"): 250,
        ("ilupeju", "mushin"): 150,
        ("ilupeju", "costain"): 200,
        ("ilupeju", "oshodi"): 250,
        ("ilupeju", "yaba"): 300,
        ("oshodi", "mushin"): 200,
        ("oshodi", "costain"): 250,
        ("oshodi", "ilupeju"): 300,
        ("oshodi", "yaba"): 350,
        ("yaba", "mushin"): 250,
        ("yaba", "costain"): 300,
        ("yaba", "ilupeju"): 350,
        ("yaba", "oshodi"): 400,
    }

    if (from_loc.lower(), to_loc.lower()) in prices:
        price = prices[(from_loc.lower(), to_loc.lower())]
        print(price)
        return Response({'price': price}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid locations'})

    
@api_view(['GET'])
def get_all_users(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)  # Serialize the queryset
    return Response({'users': serializer.data}, status=status.HTTP_200_OK)