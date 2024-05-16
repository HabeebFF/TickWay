from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Ticket, Wallet, Transaction
from .serializers import UserSerializer, TicketSerializer
from django.contrib.auth import authenticate
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import paystack
import requests
import json


paystack_secret_key = 'sk_test_c70a285be29337a0697e19864e3665adb79cfc37'
paystack.api_key = paystack_secret_key


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        username = user.username
        user_det = Users.objects.get(username=username)
        user_id = user_det.user_id
        # print(user_id)
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

    user = Users.objects.filter(email=email, password=password)

    if user:
        user_info = {}
        for info in user:
            user_info["user_id"] = info.user_id
            user_info["username"] = info.username
            user_info["first_name"] = info.first_name
            user_info["last_name"] = info.last_name
            user_info["email"] = info.email
            user_info["phone_number"] = info.phone_number

        # User is authenticated, return success response
        return Response({'message': 'Login successful', "user_info": user_info}, status=status.HTTP_200_OK)
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

                wallet.wallet_balance = float(wallet.wallet_balance) - price
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
    trip_type = request.data.get('trip_type')

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
        # print(price)
        if trip_type == "one_way":
            return Response({'price': price}, status=status.HTTP_200_OK)
        elif trip_type == "round_trip":
            price = price * 2

            price = price - (price * 0.15)
            return Response({'price': price}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid locations'})

    
@api_view(['GET'])
def get_all_users(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)  # Serialize the queryset
    return Response({'users': serializer.data}, status=status.HTTP_200_OK)



@csrf_exempt
def paystack_webhook(request):
    event = json.loads(request.body)

    if event['event'] == 'charge.success':
        data = event['data']
        reference = data['reference']
        amount = data['amount'] / 100  # Convert back to main currency unit

        try:
            # Retrieve the transaction record
            transaction = Transaction.objects.get(reference=reference)
            
            # Update the transaction status to successful
            transaction.transaction_status = 'success'
            transaction.save()

            # Update the user's wallet balance
            user = transaction.user_id
            wallet = Wallet.objects.select_for_update().get(user_id=user)
            wallet.wallet_balance += amount
            wallet.save()
            print("Wallet updated successfully")
        except Transaction.DoesNotExist:
            print("Transaction not found")
        except Users.DoesNotExist:
            print("User not found")
        except Wallet.DoesNotExist:
            print("Wallet not found")
        except Exception as e:
            print("Error updating wallet:", e)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def top_up_wallet(request):
    email = request.data.get("email")
    amount = request.data.get("amount")
    user_id = request.data.get("user_id")  # Assuming user_id is passed from the frontend

    if not email or not amount or not user_id:
        return Response({"error": "Email, amount, and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Convert amount to kobo (smallest currency unit)
    amount_in_kobo = int(float(amount) * 100)

    try:
        user = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Initialize transaction with Paystack
    url = "https://api.paystack.co/transaction/initialize"
    payload = json.dumps({
        "email": email,
        "amount": amount_in_kobo,
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk_test_c70a285be29337a0697e19864e3665adb79cfc37',
        'Cookie': '__cf_bm=gbrsDV91pqifBrsEGL.qw9zKSpF3Ko5OYkaIAMtnXBw-1715894815-1.0.1.1-51YT3WXxG0FaQG3S6qv0vW_QHwiTVy9eGZzAACSOH7Dfn_tVOdWK48v9XWJ2VuuFjm9KoVytG1LW8CqjGtFYPA; sails.sid=s%3AmcZ3e8mg-Bj4sBRAYJT7ECXiVOvSVAtE.SPmkE9pi9JG%2FUR%2FXTqmgD8QqaquBN9h32g7MNGIJTqA'
    }

    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()

    if response.status_code == 200 and response_data['status']:
        data = response_data['data']
        reference = data['reference']
        access_code = data['access_code']
        authorization_url = data['authorization_url']

        # Log transaction details
        Transaction.objects.create(
            user_id=user,
            reference=reference,
            transaction_type='topup',
            transaction_status='initialized',
            access_code=access_code,
            email=email,
            amount=amount,
        )

        return Response({"authorization_url": authorization_url, "access_code": access_code}, status=status.HTTP_200_OK)
    else:
        return Response(response_data, status=response.status_code)
