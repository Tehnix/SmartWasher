from app import app
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
