import DbHandler as db

class DepartmentModel:
    
    def __init__(self):
        self.table = db.resource.Table('Department')
    
    # Get all the departments in the database
    def getDepartments(self):
        response = self.table.scan()
        items = response.get('Items')
        return items
