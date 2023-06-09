import os
from flask import Blueprint, request, jsonify
from model import DepartmentModel
import requests

departmentsBlueprint = Blueprint('departments', __name__, )

# GET API to get all the departments
@departmentsBlueprint.route('/peoplesuite/apis/departments', methods=['GET'])
def getDepartment():
    departmentModel = DepartmentModel()
    department = departmentModel.getDepartments()
    if department:
        return jsonify(department), 200
    else:
        return jsonify({'message': 'Department not found'}), 404

# GET API to get all the Employees in a department
@departmentsBlueprint.route('/peoplesuite/apis/departments/<departmentId>/employees', methods=['GET'])
def getDepartmentEmployee(departmentId):
    currentDomain = os.environ.get('DOMAIN', 'http://localhost:5000')
    url = f'{currentDomain}/peoplesuite/apis/employees/{departmentId}'
    response = requests.get(url)
    # Check the response status code
    if response.status_code == 200:
        employees = response.json()
        return employees
    elif response.status_code == 404:
        return {'message': 'Department not found'}, 404

