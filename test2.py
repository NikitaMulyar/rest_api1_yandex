from requests import get, post, delete, put


print(get('http://127.0.0.1:8080/api/users').json())
print(post('http://127.0.0.1:8080/api/users', json={'email': '1@123', 'password': 'qwerty',
    'surname': 'ivanov', 'name': 'ivan', 'age': 21, 'position': 'none', 'speciality': 'mephi',
                                                    'address': 'kashirskoe shosse'}).json())
print(put('http://127.0.0.1:8080/api/users/8', json={'email': '1@123', 'password': 'qwerty',
    'surname': 'ivanov', 'name': 'ivan', 'age': 215, 'position': 'none', 'speciality': 'mephi',
                                                    'address': 'kashirskoe shosse'}).json())
print(delete('http://127.0.0.1:8080/api/users/8').json())