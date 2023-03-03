from requests import get, post

"""print(get('http://127.0.0.1:8080/api/jobs').json())
print(get('http://127.0.0.1:8080/api/jobs/2').json())
print(get('http://127.0.0.1:8080/api/jobs/342874343').json())
print(get('http://127.0.0.1:8080/api/jobs/eee').json())"""
print(post('http://127.0.0.1:8080/api/jobs',
           json={"id": 1, "team_leader_email": "1233@123", "title": "testing", "work_size": 16,
                 "hazard_level": 9, "collaborators": None,
                  "start_date": None, "end_date": None, "is_finished": True}).text)
