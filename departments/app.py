from flask import Flask
from routes import departmentsBlueprint

app = Flask(__name__)

# Register the departments blueprint
app.register_blueprint(departmentsBlueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)