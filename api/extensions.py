from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

cors = CORS()
db = SQLAlchemy()
mail = Mail()
