# from dotenv import load_dotenv
from decouple import config
from flask import Flask, render_template, request

from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user

# load_dotenv()

def create_app():
    """Creates and configures Flask app instance"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)


    @app.route('/')
    def root():
        # DB.create_all()
        return render_template('base.html', title="Home", users=User.query.all())

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['username']
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = f'User {name} successfully added!'
            tweets = User.query.filter(User.username==name).one().tweets
        except Exception as e:
            message = f'Error while trying to add user {name}: {e}'
            tweets = []
        return render_template('user.html', title=name, message=message, tweets=tweets)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset database!')


    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2, request.values['tweet_text'])
            message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1)
        return render_template('prediction.html', title='Prediction', message=message)

    return app