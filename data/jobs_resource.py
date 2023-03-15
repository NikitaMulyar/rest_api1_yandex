from flask_restful import Resource
from . import db_session
from .jobs import Jobs
from flask import abort, jsonify
from .parse_jobs import parser
from .category import Category
from datetime import datetime


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    news = session.query(Jobs).get(job_id)
    if not news:
        abort(404, description=f'Job {job_id} not found.')


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'jobs': job.to_dict()})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'news': [item.to_dict() for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        job = Jobs()
        job.job = args['job']
        job.team_leader = args['team_leader']
        job.is_finished = args['is_finished']
        job.start_date = datetime.fromisoformat(args['start_date'])
        job.end_date = datetime.fromisoformat(args['end_date'])
        job.collaborators = args['collaborators']
        job.work_size = args['work_size']
        categ = Category()
        categ.level = args['hazard_level']
        job.categories.append(categ)

        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
