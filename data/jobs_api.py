import flask
from flask import request, jsonify
from . import db_session
from .jobs import Jobs
from .users import User


blueprint = flask.Blueprint('jobs_api', __name__, template_folder='templates')


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify({'jobs': [item.to_dict() for item in jobs]})


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(job_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'job': jobs.to_dict()
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader_email', 'title', 'work_size', 'hazard_level', 'collaborators',
                  'start_date', 'end_date', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    if 'id' in request.json:
        id_ = db_sess.query(Jobs).filter(Jobs.id == request.json['id']).first()
        if id_:
            return jsonify({'error': 'Id already exists'})
    id_ = db_sess.query(User).filter(User.email == request.json['team_leader_email']).first()
    if not id_:
        return jsonify({'error': 'Bad request'})
    job = Jobs()
    job.job = request.json['title']
    job.team_leader = id_.id
    job.id = request.json['id']
    job.work_size = request.json['work_size']
    job.collaborators = request.json['collaborators']
    job.start_date = request.json['start_date']
    job.end_date = request.json['end_date']
    job.is_finished = request.json['is_finished']
    job.hazard_level = request.json['hazard_level']
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})
