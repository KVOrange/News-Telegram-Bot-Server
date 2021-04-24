from flask import Flask

import config
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    import app.api.user as user
    import app.api.subscriptions as subscriptions
    import app.api.news as news

    app.register_blueprint(user.module)
    app.register_blueprint(subscriptions.module)
    app.register_blueprint(news.module)

    return app
