import requests
BASE_URL = 'http://localhost:5000'

def test_get_user_intervals():
    response = requests.get('http://localhost:5000/user_intervals')
    assert response.status_code == 200


def test_get_user_list():
    response = requests.get('http://localhost:5000/api/users/list')
    assert response.status_code == 200


def test_invalid_endpoint():
    response = requests.get(f'{BASE_URL}/nonexistent_endpoint')


    assert response.status_code == 404
