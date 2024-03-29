import datetime
from requests import get
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, BooleanField, StringField, IntegerField, \
    DateTimeField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired

from data import db_session, jobs_api, users_api
from data.departments import Department
from data.jobs import Jobs
from data.news import News
from data.users import User
from data.category import Category
from flask_restful import abort, Api
from data.users_resource import UsersResource, UsersListResource
from data.news_resource import NewsResource, NewsListResource
from data.jobs_resource import JobsResource, JobsListResource


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age')
    pos = StringField('Position')
    spec = StringField('Speciality')
    adrs = StringField("Address")
    city = StringField("Hometown", validators=[DataRequired()])
    submit = SubmitField('Register')


class JobForm(FlaskForm):
    email = SelectField('Team leader email', choices=[], validators=[DataRequired()])
    name = StringField('Title of job', validators=[DataRequired()])
    w_size = IntegerField('Work size (in hours)', validators=[DataRequired()])
    collab = SelectMultipleField('Collaborators\' IDs', choices=[])
    start_date = DateTimeField('Start date', format='%Y-%m-%d %H:%M:%S',
                             default=datetime.datetime(year=2023, month=2, day=25, hour=12, minute=0, second=0))
    end_date = DateTimeField('End date', format='%Y-%m-%d %H:%M:%S',
                             default=datetime.datetime(year=2024, month=2, day=25, hour=12, minute=0, second=0))
    hazard_level = IntegerField('Hazard level', default=None)
    done = BooleanField('Is finished?')
    submit = SubmitField('Submit')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class DepartmentForm(FlaskForm):
    title = StringField('Department name', validators=[DataRequired()])
    email = SelectField('Chief email', choices=[], validators=[DataRequired()])
    email_dep = EmailField('Department email', validators=[DataRequired()])
    members = SelectMultipleField('Members\' IDs', choices=[])
    submit = SubmitField('Submit')


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def base():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template('common.html', news=news)


@app.route('/jobs')
def list_jobs():
    db_sess = db_session.create_session()
    res = db_sess.query(Jobs).all()
    data = []
    for job in res:
        title = job.job
        time = f'{round((job.end_date - job.start_date).total_seconds() / 3600)} hours'
        user_id = -1
        if job.user is None:
            team_leader = 'User doesn\'t exist'
        else:
            team_leader = job.user.name + ' ' + job.user.surname
            user_id = job.user.id
        collab = job.collaborators
        f = job.is_finished
        lvl = job.categories[-1].level if len(job.categories) else None
        data.append([title, team_leader, time, collab, f, user_id, job.id, lvl])
    return render_template('jobs.html', jobs=data)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register form',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register form',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.pos.data,
            address=form.adrs.data,
            speciality=form.spec.data,
            city_from=form.city.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Register form', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def addjob():
    form = JobForm()
    _tmp = db_session.create_session()
    _res = _tmp.query(User).all()
    for _i in _res:
        form.email.choices.append(_i.email)
        form.collab.choices.append(str(_i.id))
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            job = Jobs()
            job.job = form.name.data
            job.team_leader = user.id
            job.collaborators = ','.join(form.collab.data)
            job.is_finished = form.done.data
            job.start_date = form.start_date.data
            job.end_date = form.end_date.data
            job.work_size = form.w_size.data
            categ = Category()
            categ.level = form.hazard_level.data
            job.categories.append(categ)
            db_sess.add(job)
            db_sess.commit()
            return redirect("/jobs")
        return render_template('job_add.html',
                               message="Неправильный адрес почты тимлида",
                               form=form)
    return render_template('job_add.html', title='Добавление работы', form=form)


@app.route('/addjob/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobForm()
    _tmp = db_session.create_session()
    _res = _tmp.query(User).all()
    for _i in _res:
        form.email.choices.append(_i.email)
        form.collab.choices.append(str(_i.id))
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter((Jobs.id == id),
                                         ((Jobs.user == current_user) | (current_user.id == 1))
                                         ).first()
        if job:
            form.name.data = job.job
            form.w_size.data = job.work_size
            # form.collab.data = job.collaborators
            form.start_date.data = job.start_date
            form.end_date.data = job.end_date
            form.email.data = job.user.email
            form.done.data = job.is_finished
            if len(job.categories):
                form.hazard_level.data = job.categories[-1].level
            else:
                form.hazard_level.data = None
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter((Jobs.id == id),
                                         ((Jobs.user == current_user) | (current_user.id == 1))
                                         ).first()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('job_add.html', title='Редактирование работы',
                                   message='Неверно указана почта тимлида', form=form)
        if job:
            job.job = form.name.data
            job.team_leader = user.id
            job.collaborators = ','.join(form.collab.data)
            job.is_finished = form.done.data
            job.start_date = form.start_date.data
            job.end_date = form.end_date.data
            job.work_size = form.w_size.data
            cat = Category()
            cat.level = form.hazard_level.data
            job.categories.append(cat)
            db_sess.commit()
            return redirect('/jobs')
        else:
            abort(404)
    return render_template('job_add.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter((Jobs.id == id),
                                      ((Jobs.user == current_user) | (current_user.id == 1))
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.user_id = current_user.id
        # current_user.news.append(news)
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter((News.id == id),
                                          ((News.user == current_user) | (current_user.id == 1))
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter((News.id == id),
                                          ((News.user == current_user) | (current_user.id == 1))
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter((News.id == id),
                                      ((News.user == current_user) | (current_user.id == 1))
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_depart():
    form = DepartmentForm()
    _tmp = db_session.create_session()
    _res = _tmp.query(User).all()
    for _i in _res:
        form.email.choices.append(_i.email)
        form.members.choices.append(str(_i.id))
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        depart = Department()
        depart.title = form.title.data
        depart.members = ','.join(form.members.data)
        depart.email = form.email_dep.data
        res = db_sess.query(User).filter(User.email == form.email.data).first()
        if res:
            depart.chief = res.id
            db_sess.add(depart)
            db_sess.commit()
            return redirect('/departments')
        return render_template('add_depart.html', title='Add a department',
                               form=form, message='Нет пользователя с таким email')
    return render_template('add_depart.html', title='Add a department',
                           form=form)


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_depart(id):
    form = DepartmentForm()
    _tmp = db_session.create_session()
    _res = _tmp.query(User).all()
    for _i in _res:
        form.email.choices.append(_i.email)
        form.members.choices.append(str(_i.id))
    if request.method == "GET":
        db_sess = db_session.create_session()
        depart = db_sess.query(Department).filter((Department.id == id),
                                                  ((Department.user == current_user) | (current_user.id == 1))).first()
        if depart:
            form.title.data = depart.title
            # form.members.data = ', '.join(depart.members)
            form.email_dep.data = depart.email
            form.email.data = depart.user.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        depart = db_sess.query(Department).filter((Department.id == id),
                                                  ((Department.user == current_user) | (current_user.id == 1))).first()
        if depart:
            depart.title = form.title.data
            depart.members = ','.join(form.members.data)
            depart.email = form.email_dep.data
            res = db_sess.query(User).filter(User.email == form.email.data).first()
            if res:
                depart.chief = res.id
                db_sess.add(depart)
                db_sess.commit()
                return redirect('/departments')
            abort(404)
    return render_template('add_depart.html', title='Department\'s editing', form=form)


@app.route('/depart_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def depart_delete(id):
    db_sess = db_session.create_session()
    depart = db_sess.query(Department).filter((Department.id == id),
                                              ((Department.user == current_user) | (current_user.id == 1))).first()
    if depart:
        db_sess.delete(depart)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/departments')
def list_departs():
    db_sess = db_session.create_session()
    res = db_sess.query(Department).all()
    return render_template('departments.html', departs=res)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/users_show/<int:user_id>')
def user_show(user_id):
    info = get(f'http://127.0.0.1:8080/api/users/{user_id}').json().get('user')
    if info is not None:
        res = get(f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={info["city_from"]}&format=json')
        pos = ",".join(res.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split())
        map_params = {
            "ll": pos,
            "l": 'sat',
            "z": '14'
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = get(map_api_server, params=map_params)
        map_file = f"static/img/map.png"
        with open(map_file, mode="wb") as file:
            file.write(response.content)
    f = info is None
    return render_template('nostalgy.html', data=info, flag=f)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    # для списка объектов
    api.add_resource(NewsListResource, '/api/v2/news')
    # для одного объекта
    api.add_resource(NewsResource, '/api/v2/news/<int:news_id>')
    # для списка объектов
    api.add_resource(UsersListResource, '/api/v2/users')
    # для одного объекта
    api.add_resource(UsersResource, '/api/v2/users/<int:user_id>')
    # для списка объектов
    api.add_resource(JobsListResource, '/api/v2/jobs')
    # для одного объекта
    api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')
    app.run(port=8080, host='127.0.0.1')
