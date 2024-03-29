import os
from flask import Blueprint, make_response, request, jsonify
from model import EmployeeModel
import DbHandler as db

employeesBlueprint = Blueprint('employees', __name__)

# GET API to perform health check in target group
@employeesBlueprint.route('/peoplesuite/apis/employees', methods=['GET'])
def healthCheck():
    return jsonify({'message': 'Health check successful' }), 200

# Endpoint for the client to send API Key and Secret to obtain an access token
@employeesBlueprint.route('/peoplesuite/apis/employees/oauth/token', methods=['POST'])
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

# GET API to get an Employee's profile
@employeesBlueprint.route('/peoplesuite/apis/employees/<employeeId>/profile', methods=['GET'])
def getEmployee(employeeId):
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    employeeId = int(employeeId)
    employeeModel = EmployeeModel()
    employee = employeeModel.getEmployee(employeeId)
    if employee == "EMPLOYEE_NOT_FOUND":
        return jsonify({'message': 'Employee not found' }), 404
    return jsonify(employee), 200

# POST API to get create Employee's profile
@employeesBlueprint.route('/peoplesuite/apis/employees/<employeeId>/profile', methods=['POST'])
def createEmployee(employeeId):
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    employeeId = int(employeeId)
    employeeData = request.json
    employeeModel = EmployeeModel()
    result = employeeModel.checkIfAnyFieldEmpty(employeeId, employeeData)
    if not result[0]:
        return jsonify({'message': result[1]}), 400
    employee = employeeModel.createEmployee(employeeId, employeeData)
    if employee  == "EMPLOYEE_ALREADY_EXISTS":
        return jsonify({'message': f'Employee with {employeeId} already exists'}), 409
    return jsonify({
                'message': 'Employee created successfully',
                'employee': employee
            }), 200

# GET API to get an Employee's photo
@employeesBlueprint.route('/peoplesuite/apis/employees/<employeeId>/photo', methods=['GET'])
def getEmployeePhoto(employeeId):
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    employeeModel = EmployeeModel()
    employee = employeeModel.getEmployee(int(employeeId))
    
    if employee is None:
        return jsonify({'message': 'Employee not found'}), 404
    
    photoData = employeeModel.getPhotoFromS3(employeeId)
    
    if photoData is None:
        return jsonify({'message': 'Photo not found for the employee'}), 404
    
    response = make_response(photoData)
    response.headers.set('Content-Type', 'image/jpeg')
    
    return response
       
# PUT API to update an Employee's photo
@employeesBlueprint.route('/peoplesuite/apis/employees/<employeeId>/photo', methods=['PUT'])
def updateEmployeePhoto(employeeId):
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token != db.ACCESS_TOKEN:
        return jsonify({'error': 'Invalid access token'}), 401
    employeeModel = EmployeeModel()
    employee = employeeModel.getEmployee(int(employeeId))
    if employee == "EMPLOYEE_NOT_FOUND":
        return jsonify({'message': 'Employee not found' }), 404
    
    if 'image' not in request.files:
        return jsonify({'message': 'Photo file/s not found in the request'}), 400
    
    photoFile = request.files['image']
    try:
        employeeModel.uploadPhotoToS3(photoFile, employeeId)
        return jsonify({'message': 'Photo uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error uploading employee photo'}), 500

# GET API to get a list of employees in a department
@employeesBlueprint.route('/peoplesuite/apis/employees/<departmentId>', methods=['GET'])
def getEmployeesByDepartment(departmentId):

    employeeModel = EmployeeModel()
    employees = employeeModel.getEmployeesByDepartment(departmentId)
    response = []

    for employee in employees:
        employeeId = employee['employeeId']
        employeeName = employee['firstName'] + ' ' + employee['lastName']
        currentDomain = os.environ.get('DOMAIN', 'http://localhost:5000')
        profileUrl = f'{currentDomain}/peoplesuite/apis/employees/' + str(employee['employeeId']) + '/profile'
        updatedEmployee = {
            'employeeId': employeeId,
            'employeeName': employeeName,
            'employeeProfileUrl': profileUrl
        }
        response.append(updatedEmployee)
    return jsonify(response), 200