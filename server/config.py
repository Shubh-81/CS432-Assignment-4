#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@localhost/maintainence'
import urllib.parse
encoded_password = urllib.parse.quote_plus('Atal@2207')

# Construct the updated SQLAlchemy database URI
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{encoded_password}@localhost/maintenance'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'inwowmew'
WTF_CSRF_ENABLED = True