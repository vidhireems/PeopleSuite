import os
from flask import Blueprint, request, jsonify
from model import DepartmentModel
import requests
import DbHandler as db

departmentsBlueprint = Blueprint('departments', __name__, )

# Endpoint for the client to send API Key and Secret to obtain an access token
@departmentsBlueprint.route('/peoplesuite/apis/departments/oauth/token', methods=['POST'])
def get_access_token():
    if request.json['api_key'] == db.API_KEY and request.json['api_secret'] == db.API_SECRET:
        access_token = db.ACCESS_TOKEN
        expires_in = 3600  # Token expiration time in seconds
        
        response = {
            'access_token': access_token,
            'expires_in': expires_in
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# GET API to get all the departments
@departmentsBlueprint.route('/peoplesuite/apis/departments', methods=['GET'])
def getDepartment():
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    departmentModel = DepartmentModel()
    department = departmentModel.getDepartments()
    if department:
        return jsonify(department), 200
    else:
        return jsonify({'message': 'Department not found'}), 404

# GET API to get all the Employees in a department
@departmentsBlueprint.route('/peoplesuite/apis/departments/<departmentId>/employees', methods=['GET'])
def getDepartmentEmployee(departmentId):
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    currentDomain = os.environ.get('DOMAIN', 'http://localhost:5000')
    url = f'{currentDomain}/peoplesuite/apis/employees/{departmentId}'
    response = requests.get(url)
    # Check the response status code
    if response.status_code == 200:
        employees = response.json()
        return employees
    elif response.status_code == 404:
        return {'message': 'Department not found'}, 404

