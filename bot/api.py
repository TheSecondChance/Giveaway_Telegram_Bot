import requests
from rest_framework import status
from rest_framework.response import Response
from typing import Optional, Dict, Any

BASE_URL = 'http://127.0.0.1:8000/'

def status(status):
    pass

def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by telegram id.
    
    Args:
        telegram_id (int): The user's Telegram ID.
    
    Returns:
        Optional[Dict[str, Any]]: The user data in a dictionary if found, None otherwise.
    """
    params = {
        'telegram_id': telegram_id
    }

    response = requests.get(BASE_URL + "api/get-telegram-id/", params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def create_user(created_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a new user by sending a POST request.

    Args:
        created_data (Dict[str, Any]): A dictionary containing the user data to create.

    Returns:
        Optional[Dict[str, Any]]: The created user data if the request is successful,
        or an error message if something goes wrong.
    """
    response = requests.post(BASE_URL + 'api/create-user/', json=created_data)

    if response.status_code == 201:
        return response.json() 
    elif response.status_code == 404:
        return {"detail": "Error not Found", "status": 404}
    elif response.status_code == 400:
        return {"detail": "Bad request", "status": 400}
    else:
        print(f"Something went wrong in create: {response.status_code} - {response.text}")
        return None

def update_user(telegram_id: int, updated_data: dict) -> Optional[Dict[str, Any]]:
    """Update user by send PUT request.

    Args:
        telegram_id (int): The user's Telegram ID.
        updated_data (dict): A dictionary containing the user data to update.

    Returns:
        Returns:
        Optional[Dict[str, any]]: The updated user data if the request is successful,
        or an error message if something goes wrong.
    """

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
