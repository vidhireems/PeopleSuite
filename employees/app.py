from flask import Flask
from routes import employeesBlueprint

app = Flask(__name__)

# Register the employees blueprint
app.register_blueprint(employeesBlueprint)

if __name__ == '__main__':
    app.run()