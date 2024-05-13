from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Ticket
from .serializers import UserSerializer
from django.contrib.auth import authenticate

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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


    if trip_type == 'one_way':
        new_ticket = Ticket(user_id=user_id, trip_type=trip_type, from_loc=from_loc, to_loc=to_loc, transport_date=transport_date, number_of_tickets=number_of_tickets, price=price)

        return Response({'message': 'One Way Ticket Purchased'}, status=status.HTTP_200_OK)
    elif trip_type == 'round_trip':
        new_ticket = Ticket(user_id=user_id, trip_type=trip_type, from_loc=from_loc, to_loc=to_loc, transport_date=transport_date, number_of_tickets=number_of_tickets, price=price)

        return Response({'message': 'Round Trip Ticket Purchased'}, status=status.HTTP_200_OK)

    else:
        return Response({'message': 'Ticket Purchase Failed'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def history(request):
    user_id = request.data.get('user_id')

    user_tickets = Ticket.objects.filter(user_id=user_id)
    print(user_tickets)

    return Response({'message': 'One Way Ticket Purchased'}, status=status.HTTP_200_OK)

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
        return Response({'price': price})
    else:
        return Response({'error': 'Invalid locations'})

    