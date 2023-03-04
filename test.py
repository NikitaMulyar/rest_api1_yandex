from requests import get, post, delete

print(get('http://127.0.0.1:8080/api/jobs').json())
print(get('http://127.0.0.1:8080/api/jobs/2').json())
print(get('http://127.0.0.1:8080/api/jobs/342874343').json())
print(get('http://127.0.0.1:8080/api/jobs/eee').json())
print(post('http://127.0.0.1:8080/api/jobs',
           json={"id": 1, "team_leader_email": "1233@123", "title": "testing", "work_size": 16,
                 "hazard_level": 9, "collaborators": None,
                  "start_date": None, "end_date": None, "is_finished": True}).json())
print(post('http://127.0.0.1:8080/api/jobs',
           json={"id": 1, "team_leader_email": "1233@123", "title": "testing", "work_size": 16,
                 "hazard_level": 9, "collaborators": None,
                  "start_date": None, "end_date": None, "is_finished": True}).json())
# Создаем дубликат с таким же id - ошибка
print(post('http://127.0.0.1:8080/api/jobs',
           json={"id": 1, "team_leader_email": "12333@123", "title": "testing", "work_size": 16,
                 "hazard_level": 9, "collaborators": None,
                  "start_date": None, "end_date": None, "is_finished": True}).json())
# Нет юзера с такой почтой - ошибка
print(post('http://127.0.0.1:8080/api/jobs',
           json={"id": 1, "team_leader_email": "12333@123", "work_size": 16,
                 "hazard_level": 9, "collaborators": None,
                  "start_date": None, "end_date": None, "is_finished": True}).json())
# Нет заголовка - ошибка
print(get('http://127.0.0.1:8080/api/jobs').json())
print(delete('http://127.0.0.1:8080/api/jobs/3').json())
print(get('http://127.0.0.1:8080/api/jobs').json())

