import requests
import streamlit as st

def login(email, password, platform='EU'):
    """
    Authenticates a user via OpenID Connect and returns auth headers.

    Args:
        email (str): User's email.
        password (str): User's password.
        platform (str): One of 'EU', 'AUS', 'USA'.

    Returns:
        dict: Headers containing the access token.
    """

    # URLs par plateforme
    url_map = {
        "EU": 'https://sso.beyond-suite.com/realms/prod-eu/protocol/openid-connect/token',
        "AUS": 'https://sso.beyond-suite.com.au/realms/prod-au/protocol/openid-connect/token',
        "USA": 'https://sso.beyond-suite.co/realms/prod-us/protocol/openid-connect/token',
    }
    url = url_map.get(platform, url_map["EU"])

    data = {
        "client_id": 'app-bm-api',
        "grant_type": 'password',
        "username": email,
        "password": password,
    }

    try:
        response = requests.post(url, data=data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        st.stop()

    if response.status_code == 401:
        st.error("Identifiants incorrects. Veuillez réessayer.")
        st.stop()

    if response.status_code != 200:
        st.error(f"Erreur API : {response.status_code} - {response.text}")
        st.stop()

    response_data = response.json()
    access_token = response_data.get("access_token")

    if not access_token:
        st.error("Token non trouvé dans la réponse.")
        st.stop()

    return {
        'accept': 'application/json',
        'authorization': f'Bearer {access_token}',
        'x-auth-request-access-token': access_token,
        'sxd-application': 'beyond-monitoring'
    }
