from flask_script import Manager
from newsapi import NewsApiClient

import config
from app import create_app

app = create_app()
app.config.from_object(config.Config)
manager = Manager(app)



if __name__ == '__main__':
    manager.run()