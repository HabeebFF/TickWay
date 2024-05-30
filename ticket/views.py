from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Ticket, Wallet, Transaction
from .serializers import UserSerializer, TicketSerializer, WalletSerializer, GetUserSerializer, TransactionSerializer
from django.contrib.auth import authenticate
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import paystack
import requests
import json
import random
import string
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

paystack_secret_key = 'sk_test_c70a285be29337a0697e19864e3665adb79cfc37'
paystack.api_key = paystack_secret_key



def generate_random_string(length=10):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# random_string = generate_random_string()


def index(request):
    return render(request, 'index.html')

# @api_view(['POST'])
# def signup(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         username = user.username
#         user_det = Users.objects.get(username=username)
#         user_id = user_det.user_id
#         # print(user_id)
#         wallet = Wallet(user_id=user_det)
#         try:
#             wallet.save()
#             print("Wallet saved successfully")
#         except Exception as e:
#             print("Error saving wallet:", e)
#         send_mail(
#             'Verify your email',
#             f'Click the following link to verify your email:',
#             settings.EMAIL_HOST_USER,
#             [user.email],
#             fail_silently=False,
#         )
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate and save verification token
        token = get_random_string(length=6)
        user.verification_token = token
        user.save()


        # Create wallet for the user
        user_det = Users.objects.get(username=user.username)
        wallet = Wallet(user_id=user_det)
        try:
            wallet.save()
            print("Wallet saved successfully")
        except Exception as e:
            print("Error saving wallet:", e)

        # Send verification email
        verification_url = f'https://habeeb1234.pythonanywhere.com/verify_email/'

        sender_email = 'habeebmuftau05@gmail.com'
        receiver_email = user.email
        password = 'jvbe whjo lnwe pwxu'
        subject = 'Verify Email'
        message = f'''Hi {user.username},
        Verify your email at {verification_url}

        Token: {token}'''

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, msg.as_string())

        server.quit()

        # send_mail(
        #     'Verify your email',
        #     f'Click the following link to verify your email: {verification_url}',
        #     settings.EMAIL_HOST_USER,
        #     [user.email],
        #     fail_silently=False,
        # )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_email(request):
    if request.method == "POST":
        email = request.POST['email']
        token = request.POST['token']
        try: 
            user = Users.objects.get(email=email)
            user_token = user.verification_token
            if user_token == token:
                update_user = Users.objects.select_for_update().get(email=email)
                update_user.is_verified = "True"
                update_user.save()
                
                return render(request, 'v_s.html')
            else:
                return render(request, 'v_f.html')
        except Users.DoesNotExist:
            return render(request, 'v_f.html')

    return render(request, 'verify_mail.html')


def verified(request):
    return render(request, 'v_s.html')


def not_verified(request):
    return render(request, 'v_s.html')

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = Users.objects.get(email=email, password=password)
        user_wallet = Wallet.objects.get(user_id=user.user_id)

        if user:
            if user.is_verified:
                user_info = {}

                user_info["user_id"] = user.user_id
                user_info["username"] = user.username
                user_info["first_name"] = user.first_name
                user_info["last_name"] = user.last_name
                user_info["email"] = user.email
                user_info["phone_number"] = user.phone_number
                user_info["wallet_balance"] = user_wallet.wallet_balance

                # User is authenticated, return success response
                return Response({'message': 'Login successful', "user_info": user_info}, status=status.HTTP_200_OK)
            else:
                # Email not Verified, return error response
                return Response({'message': 'User Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Authentication failed, return error response
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except Users.DoesNotExist:
        return Response({'error': 'Email or Password incorrect'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def get_user_info(request):
    user_id = request.data.get('user_id')

    try:
        user = Users.objects.get(user_id=user_id)
        user_wallet = Wallet.objects.get(user_id=user.user_id)

    except Users.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    except Wallet.DoesNotExist:
        return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # user_info = {}

    # user_info["user_id"] = user.user_id
    # user_info["username"] = user.username
    # user_info["first_name"] = user.first_name
    # user_info["last_name"] = user.last_name
    # user_info["email"] = user.email
    # user_info["phone_number"] = user.phone_number
    # user_info["wallet_balance"] = user_wallet.wallet_balance

    return Response({'wallet_balance': user_wallet.wallet_balance}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_user_info_with_username(request):
    username = request.data.get('username')

    try:
        user = Users.objects.get(username=username)
        if user:
            return Response({'username': username}, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

def convert_date_format(date_str):
    try:
        # Parse the input string to a datetime object
        input_date = datetime.strptime(date_str, "%d-%m-%Y")
        # Format the datetime object to the desired output string
        output_date = input_date.strftime("%Y-%m-%d")
        return output_date
    except ValueError:
        return "Invalid date format. Please use dd-mm-yyyy."


@api_view(['POST'])
def book_ticket(request):
    user_id = request.data.get('user_id')
    trip_type = request.data.get('trip_type')
    from_loc = request.data.get('from_loc')
    to_loc = request.data.get('to_loc')
    transport_date = request.data.get('transport_date')
    price = request.data.get('price')

    if None in [user_id, trip_type, from_loc, to_loc, transport_date, price]:
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

                Ticket.objects.create(
                    user_id=user,
                    trip_type=trip_type,
                    from_loc=from_loc,
                    to_loc=to_loc,
                    transport_date=convert_date_format(transport_date),
                    price=price
                )

                # booked_ticket = {
                #     "user_id": user_id,
                #     "trip_type": trip_type,
                #     "from_loc": from_loc,
                #     "to_loc": to_loc,
                #     "transport_date": transport_date,
                #     "price":price
                # }

                return Response({"message": "Booking Successful"}, status=status.HTTP_200_OK)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif trip_type == 'round_trip':
        with transaction.atomic():
            try:
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)
                if wallet.wallet_balance < price:
                    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

                wallet.wallet_balance = float(wallet.wallet_balance) - price
                wallet.save()

                Ticket.objects.create(
                    user_id=user,
                    trip_type=trip_type,
                    from_loc=from_loc,
                    to_loc=to_loc,
                    transport_date=convert_date_format(transport_date),
                    price=price
                )

                # booked_ticket = {
                #     "user_id": user_id,
                #     "trip_type": trip_type,
                #     "from_loc": from_loc,
                #     "to_loc": to_loc,
                #     "transport_date": transport_date,
                #     "price":price
                # }
                return Response({"message": "Booking Successful"}, status=status.HTTP_200_OK)
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


@api_view(['GET'])
def get_all_tickets(request):
    tickets = Ticket.objects.all()
    serializer = TicketSerializer(tickets, many=True)

    return Response({'user_tickets': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_transactions(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many=True)

    return Response({'all_transactions': serializer.data}, status=status.HTTP_200_OK)


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
    serializer = GetUserSerializer(users, many=True)  # Serialize the queryset
    wallets = Wallet.objects.all()
    wallet_serializer = WalletSerializer(wallets, many=True)
    return Response({'users': serializer.data, 'wallet': wallet_serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def verify_payment(request):
    reference = request.data.get('reference')
    amount = request.data.get('amount')

    if not reference:
        return Response({'error': 'Reference is required.'}, status=status.HTTP_400_BAD_REQUEST)

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk_test_c70a285be29337a0697e19864e3665adb79cfc37'
    }

    response = requests.get(url, headers=headers)
    # print(response.text)

    if response.status_code == 200:
        response_data = response.json()
        print(response_data['status'])
        print(response_data['data']['amount'])
        if response_data['status'] and response_data['data']['amount'] == int(amount) * 100:
            print('good')
            try:
                # Retrieve the transaction record
                transaction = Transaction.objects.get(reference=reference)

                # Update the transaction status to successful
                transaction.transaction_status = 'success'
                transaction.save()

                # Update the user's wallet balance
                user = transaction.user_id
                wallet = Wallet.objects.select_for_update().get(user_id=user)
                wallet.wallet_balance += int(amount)
                wallet.save()
                print("Wallet updated successfully")
            except Transaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print("Error updating wallet:", e)
                return Response({'error': 'Error updating wallet'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'Payment verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Failed to verify payment.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @csrf_exempt
# def paystack_webhook(request):
#     event = json.loads(request.body)

#     if event['event'] == 'charge.success':
#         data = event['data']
#         reference = data['reference']
#         amount = data['amount'] / 100  # Convert back to main currency unit

#         try:
#             # Retrieve the transaction record
#             transaction = Transaction.objects.get(reference=reference)

#             # Update the transaction status to successful
#             transaction.transaction_status = 'success'
#             transaction.save()

#             # Update the user's wallet balance
#             user = transaction.user_id
#             wallet = Wallet.objects.select_for_update().get(user_id=user)
#             wallet.wallet_balance += amount
#             wallet.save()
#             print("Wallet updated successfully")
#         except Transaction.DoesNotExist:
#             print("Transaction not found")
#         except Users.DoesNotExist:
#             print("User not found")
#         except Wallet.DoesNotExist:
#             print("Wallet not found")
#         except Exception as e:
#             print("Error updating wallet:", e)

#     return Response(status=status.HTTP_200_OK)


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
            transaction_status='pending',
            access_code=access_code,
            email=email,
            amount=amount,
        )

        return Response({"authorization_url": authorization_url, "access_code": access_code, "reference": reference, "amount": amount}, status=status.HTTP_200_OK)
    else:
        return Response(response_data, status=response.status_code)


@api_view(['POST'])
def change_username(request):
    new_username = request.data.get("new_username")
    user_id = request.data.get("user_id")

    if not new_username or not user_id:
        return Response({'message': 'new_username and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            if Users.objects.filter(username=new_username).exists():
                return Response({'message': 'Username has been taken'}, status=status.HTTP_400_BAD_REQUEST)

            user = Users.objects.select_for_update().get(user_id=user_id)
            user.username = new_username
            user.save()

            return Response({'message': 'Username updated successfully'}, status=status.HTTP_200_OK)

    except Users.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def change_email(request):
    new_email = request.data.get("new_email")
    user_id = request.data.get("user_id")

    if not new_email or not user_id:
        return Response({'message': 'new_email and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            if Users.objects.filter(email=new_email).exists():
                return Response({'message': 'Email has been taken'}, status=status.HTTP_400_BAD_REQUEST)

            user = Users.objects.select_for_update().get(user_id=user_id)
            user.email = new_email
            user.save()

            return Response({'message': 'Email updated successfully'}, status=status.HTTP_200_OK)

    except Users.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def change_phone_number(request):
    new_phone_number = request.data.get("new_phone_number")
    user_id = request.data.get("user_id")

    if not new_phone_number or not user_id:
        return Response({'message': 'new_phone_number and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            if Users.objects.filter(phone_number=new_phone_number).exists():
                return Response({'message': 'Phone number has been taken'}, status=status.HTTP_400_BAD_REQUEST)

            user = Users.objects.select_for_update().get(user_id=user_id)
            user.phone_number = new_phone_number
            user.save()

            return Response({'message': 'Phone Number updated successfully'}, status=status.HTTP_200_OK)

    except Users.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def debit_user(request):
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')

    user = Users.objects.get(user_id=user_id)

    if not user_id or not amount:
        return Response({'error': 'user_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            sender_balance = Wallet.objects.select_for_update().get(user_id=user_id)
            if sender_balance.wallet_balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            sender_balance.wallet_balance -= amount
            sender_balance.save()

            sender = Users.objects.get(user_id=user_id)
            sender_email = sender.email

            reference = generate_random_string()
            access_code = generate_random_string(5)

            Transaction.objects.create(
                user_id=user,
                reference=reference,
                transaction_type='transfer',
                transaction_status='pending',
                access_code=access_code,
                email=sender_email,
                amount=amount,
            )

            return Response({'reference': reference, 'amount': amount}, status=status.HTTP_200_OK)
    except Wallet.DoesNotExist:
        return Response({'error': 'Sender wallet not found'}, status=status.HTTP_404_NOT_FOUND)
    except Users.DoesNotExist:
        return Response({'error': 'Sender user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def credit_user(request):
    receiver_username = request.data.get('receiver_username')
    reference = request.data.get('reference')
    amount = request.data.get('amount')

    if not receiver_username or not reference or not amount:
        return Response({'error': 'receiver_username, reference, and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:

            transaction = Transaction.objects.select_for_update().get(reference=reference, amount=amount, transaction_status='pending')

            receiver = Users.objects.get(username=receiver_username)
            receiver_balance = Wallet.objects.select_for_update().get(user_id=receiver.user_id)
            receiver_balance.wallet_balance += amount
            receiver_balance.save()

            transaction.transaction_status = 'success'
            transaction.save()

            return Response({'message': 'Transfer Successful'}, status=status.HTTP_200_OK)
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found or invalid amount'}, status=status.HTTP_404_NOT_FOUND)
    except Users.DoesNotExist:
        return Response({'error': 'Receiver user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Wallet.DoesNotExist:
        return Response({'error': 'Receiver wallet not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
