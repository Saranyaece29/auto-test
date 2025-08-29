# python tests/test_src/test_routers/get_token.py
import requests


def get_tokens():
    """Log in and return an access token.

    Returns
    -------
    dict
        A dictionary containing the access token details.

    """
    host_url = "http://127.0.0.1:8001"

    login_url = f"{host_url}/v1/authorization/login"

    login_payload = {
        "username": "cwalters@fido.tech",
        "password": "!Carl123456",
    }

    login_response = requests.post(login_url, data=login_payload, verify=False)

    login_response.raise_for_status()
    token = login_response.json()

    if not token:
        raise ValueError("Access token not found in the login response.")
    return token


print(get_tokens())
