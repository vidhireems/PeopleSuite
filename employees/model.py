from datetime import datetime
import pycountry
import DbHandler as dbInstance
import botocore
from boto3.dynamodb.conditions import Attr



class EmployeeModel:
    def __init__(self):
        self.table = dbInstance.resource.Table('Employee')
        self.bucketName = dbInstance.BUCKET_NAME

    # Checks if the date is in correct format
    def validDateFormat(self, date):
        try:       
            date_obj = datetime.strptime(date, "%d/%m/%y")
            if date_obj.strftime("%d/%m/%y") == date:
                return True
        except ValueError:
            pass
    
        return False
    
    # Check if the country code is valid ISO-3166 code
    def validateCountryCode(self, countryCode):
        if pycountry.countries.get(alpha_2=countryCode.upper()):
            return True
        return False


    # Checks if any field in Employee object is empty
    def checkIfAnyFieldEmpty(self, employeeId, employeeData):

        if employeeData is None or \
           'employeeId' not in employeeData or \
            employeeData['employeeId'] is None or \
            not isinstance( employeeData['employeeId'], int) or \
            employeeId != employeeData['employeeId'] or \
            len(str(employeeData['employeeId'])) != 7:
            return [False, "Provided Employee ID is incorrect"]
        
        if 'firstName' not in employeeData or \
           'lastName' not in employeeData or \
            employeeData['firstName'] is None or \
            employeeData['lastName'] is None or \
            len(employeeData['firstName']) == 0 or \
            len(employeeData['lastName']) == 0:
            return [False, "Provided First Name or Last Name is incorrect"]
        
        if 'startDate' not in employeeData or \
            employeeData['startDate'] is None or \
            len(employeeData['startDate']) == 0 or \
            not self.validDateFormat(employeeData['startDate']):
            return [False, "Provided start date is incorrect"]
        
        if 'country' not in employeeData or \
            employeeData['country'] is None or \
            len(employeeData['country']) != 2 or \
            not self.validateCountryCode(employeeData['country']):
            return [False, "Provided country code is incorrect"]
        
        if 'departmentId' not in employeeData or \
            employeeData['departmentId'] is None or \
            len(employeeData['departmentId']) == 0:
            return [False, "Provided departmentId is empty"]
           
        if 'title' not in employeeData or \
            employeeData['title'] is None or \
            len(employeeData['title']) == 0:
            return [False, "Provided title is empty"]
        
        if 'managerId' not in employeeData:
            return [False, "Provided Manager ID is empty"]
        
        if 'managerName' not in employeeData:
            return [False, "Provided Manager Name is empty"]
        
        else:
            return  [True, "All fields were accurate"]

    # Get the Key for Employee Photo
    def getEmployeePhotoKey(self, employeeId):
        try:
            response = dbInstance.s3Client.list_objects_v2(Bucket=self.bucketName, Prefix=employeeId)
            if 'Contents' in response:
                return response['Contents'][0]['Key']
        except botocore.exceptions.BotoCoreError as e:
            raise e        
        return None

    # Upload the Employee Photo to S3
    def uploadPhotoToS3(self, photoFile, employeeId):
        try:
            photoKey = self.getEmployeePhotoKey(employeeId)
            if photoKey:
                dbInstance.s3Client.delete_object(Bucket=self.bucketName, Key=photoKey)
            dbInstance.s3Client.upload_fileobj(photoFile, self.bucketName, employeeId)
        except botocore.exceptions.NoCredentialsError as e:
            print(f"No credentials {e}")
            raise
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Endpoint error {e}")
            raise
        except botocore.exceptions.BotoCoreError  as e:
            print(f"boto core error {e}")
            raise e
        except Exception as e:
            print(f"External exception {e}")
            raise
    
    # Gets Employee Photo based on Employee ID
    def getPhotoFromS3(self, employeeId):
        try:
            response = dbInstance.s3Client.get_object(Bucket=self.bucketName, Key=employeeId)
            return response['Body'].read()
        except botocore.exceptions.BotoCoreError as e:
            raise e
           
    # Helper to generate the URL for Photo stored in S3
    def generatePhotoUrl(self, employeeId):
        photoUrl = dbInstance.s3Client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucketName, 'Key': employeeId},
            ExpiresIn=3600
        )
        return photoUrl
    
    # Get the Employee Details based on ID
    def getEmployee(self, employeeId):
        response = self.table.get_item(Key={"employeeId": employeeId})
        item = response.get('Item')
        if item:
            return item
        else:
            return "EMPLOYEE_NOT_FOUND"
        
    # Get the Employees based on department
    def getEmployeesByDepartment(self, departmentId):
        response = self.table.scan(
            FilterExpression=Attr('departmentId').eq(departmentId)
        )
        items = response.get('Items')
        return items
    
    # Add a new Employee
    def createEmployee(self, employeeId, employeeData):
        employee = self.getEmployee(employeeId)
        if employee == "EMPLOYEE_NOT_FOUND":
            response = self.table.put_item(Item=employeeData)
            return response
        else:
            return "EMPLOYEE_ALREADY_EXISTS"
    
