import requests
from rest_framework import status
from rest_framework.response import Response

BASE_URL = 'http://127.0.0.1:8000/'

def status(status):
    pass

def get_user(telegram_id: int):
    params = {
        'telegram_id': telegram_id
    }

    response = requests.get(BASE_URL + "api/get-telegram-id/", params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def create_user(created_data: dict):
    """Create User required: telegram_id"""
    response = requests.post(BASE_URL + 'api/create-user/', json=created_data)

    if response.status_code == 201:
        return response.json()
    elif response.status_code == 404:
        return Response({"detail": "Error not Found"},
                                status=status.HTTP_404_NOT_FOUND)
    elif response.status_code == 400:
        return Response({"detail": "Bad request"},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        print("Something went wrong in create", response.status_code, response.text)

def update_user(telegram_id: int, updated_data: dict):
    """update user by telegram id"""

    params = {
        'telegram_id': telegram_id
    }
    response = requests.put(
        url=BASE_URL + 'api/get-telegram-id/',
        params=params,
        json=updated_data
    )
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return Response({"detail": "No user found with the provided telegram_id"},
                        status=status.HTTP_400_BAD_REQUEST)
    elif response.status_code == 400:
        return Response({"detail": "Bad request"},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "something wrong"},  response.status_code)
