from requests import get, post, delete


print(get('http://127.0.0.1:8080/api/v2/jobs').json())
print(
    post('http://127.0.0.1:8080/api/v2/jobs', json={'team_leader': 'ee', 'job': 'test2', 'work_size': 15,
                                                    'collaborators': '1,2,3', 'start_date': '2020-12-01',
                                                    'end_date': '2023-03-18', 'hazard_level': 0,
                                                    'is_finished': False}).json())
print(
    post('http://127.0.0.1:8080/api/v2/jobs', json={'team_leader': 1, 'job': 'test2', 'work_size': 15,
                                                    'collaborators': '1,2,3', 'start_date': '2020-12-01',
                                                    'end_date': '2023-03-18', 'hazard_level': 0,
                                                    'is_finished': False}).json())
print(delete('http://127.0.0.1:8080/api/v2/jobs/10').json())
print(delete('http://127.0.0.1:8080/api/v2/jobs/11').json())
