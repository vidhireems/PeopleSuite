from flask import Blueprint, request, jsonify
from model import DepartmentModel
import requests

departmentsBlueprint = Blueprint('departments', __name__)

# GET API to get all the departments
@departmentsBlueprint.route('/departments', methods=['GET'])
def getDepartment():
    departmentModel = DepartmentModel()
    department = departmentModel.getDepartments()
    if department:
        return jsonify(department)
    else:
        return jsonify({'message': 'Department not found'}), 404

# GET API to get all the Employees in a department
@departmentsBlueprint.route('/departments/<departmentId>/employees', methods=['GET'])
def getDepartmentEmployee(departmentId):
    url = f'http://localhost:5000/employees/{departmentId}'
    response = requests.get(url)
    # Check the response status code
    if response.status_code == 200:
        employees = response.json()
        return employees
    elif response.status_code == 404:
        return {'message': 'Department not found'}, 404

