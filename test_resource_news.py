from requests import get, post, delete

print(get('http://127.0.0.1:8080/api/v2/news').json())
print(
    post('http://127.0.0.1:8080/api/v2/news', json={'title': 'test news', 'content': 'hello world!',
                                                    'is_private': False, 'user_id': 1}).json())
print(
    post('http://127.0.0.1:8080/api/v2/news', json={'title': 'test news', 'content': 'hello world!',
                                                    'is_private': False, 'user_id': 331}).json())
print(delete('http://127.0.0.1:8080/api/v2/news/3').json())
