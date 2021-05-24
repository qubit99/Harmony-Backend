import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from harmony import db, app


migrate = Migrate(app, db)
manager = Manager(app)

HRS_BASE_URL = 'http://harmony-mrs.herokuapp.com'

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
