from flask import Flask, render_template, url_for, request
from database import get_db, close_db
from forms import *

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "THIS-IS-MY-SECRET-KEY"


class Form:
    # This variable is used to track the currently rendered form. This is used to give the correct error message without moving to a new form.
    form = ""

class TableColumns:
    
    tables = ["employee","department"]
    combinedColumns = ["employee_id","name","department_id","name"]
    employeeColumns = ["employee_id","name","department_id"]
    departmentColumns = ["department_id","name"]

# Completed and Debugged
@app.route("/", methods=["GET","POST"])
def lookup():
    # A few parameters to get going
    selectionform = SelectionForm()
    noform = NoForm()
    yesform = YesForm()
    db = get_db()
    selection = ""
    success = ""
    error = ""
    # If the NoForm validates, it comes here
    if noform.validate_on_submit():
        employeeID = noform.employeeID.data
        employeeSQL = {}
        departmentSQL = {}
        # This for loop goes through the available columns and grabs all the data using the employee_id - This works as employee_id cannot be dropped.
        for column in TableColumns.employeeColumns:
            employeeData = db.execute("""SELECT %s FROM employee WHERE employee_id = ?;""" %column,(employeeID,)).fetchone()
            if employeeData != None:
                employeeSQL[column] = employeeData[0]
        if employeeData == None:
            success = "There is no employee with this employee ID"
            return render_template("index.html", form=noform, success=success, employeeData=employeeData, departmentData=None, error=error, selection="Search an Employee",headerColumns=TableColumns.combinedColumns)
        
        # This loop wants to go through the keys e.g. columns from the employee columns and checks if department_id exists and gets that name. 
        for keys_values in employeeSQL.items():
            if keys_values[0] == "department_id":
                departmentData = db.execute("""SELECT * FROM department WHERE %s = ?;""" % keys_values[0],(keys_values[1],)).fetchone()
        if departmentData != None:
            departmentSQL = dict(zip(TableColumns.departmentColumns,departmentData))
        if departmentSQL == {}:
            departmentName = "NULL"
        if 'name' in departmentSQL.keys():
            departmentName = departmentSQL["name"]
        else:
            departmentName = "NULL"

        success = "Success, here is your employee and their department."
        return render_template("index.html", form=noform, success=success, employeeID=employeeID, employeeData=employeeData,departmentName=departmentName, error=error, selection="Search an Employee",headerColumns=TableColumns.combinedColumns)
    
    # If the YesForm validates, it comes here
    if yesform.validate_on_submit():
        employeeName = yesform.employeeName.data
        departmentID = yesform.departmentID.data
        if departmentID == "" and employeeName != None:
            db.execute(""" INSERT INTO employee (name) VALUES (?);""",(employeeName,))
            db.commit()
            employeeData = db.execute("""SELECT employee_id,name,department_id FROM employee WHERE name = ? AND department_id IS NULL;""",(employeeName,)).fetchone()
            employeeID = employeeData[0]
            employeeData = [employeeData[1],"NULL"]
            departmentData = ["NULL"]
        else:
            try:
                departmentID = int(departmentID)
                if departmentID < 0:
                    error = 10/0
            except:
                error = "The Department ID needs to be a positive number. No negative numbers or Words accepted"
                employeeID = ""
                employeeData = ""
                departmentData = ""
                return render_template("index.html",form=yesform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData,error=error,selection="Add an Employee",headerColumns=TableColumns.combinedColumns)

            db.execute(""" INSERT INTO employee (name,department_id)
                                            VALUES (?,?);""",(employeeName,departmentID))
            db.commit()
            employeeData = db.execute("""SELECT employee_id,name,department_id FROM employee WHERE name = ? AND department_id = ?;""",(employeeName,departmentID)).fetchone()
            employeeID = employeeData[0]
            employeeData = [employeeData[1],employeeData[2]]
            departmentData = db.execute("""SELECT name FROM department WHERE department_id = ?;""",(employeeData[1],)).fetchone()
            if departmentData == None:
                departmentData = ["Null"]
        
        success = "Success, the employee has been added"
        return render_template("index.html",form=yesform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData,error=error,headerColumns=TableColumns.combinedColumns)
    
    # If NoForm & YesForm fail to validate - This only occurs after the selection is posted
    if (selectionform.validate_on_submit()):
        selection = selectionform.selection.data
        # If selection is contains the word "Search" - Which is the case for "Search for an employee" - Then this renders the noForm.
        # Additionally, The Form is tracked with Form.form = noForm. 
        if "Search" in selection:
            Form.form = noform
            return render_template("index.html",form=noform,success=success,selection=selection,error=error)
        # The only other option is "Add an employee" and this renders the YesForm. This also updates the Form.form variable.
        else:
            Form.form = yesform
            return render_template("index.html",form=yesform,success=success,selection=selection,error=error)

    # If the Form isn't validated and the request is POST then it checks the issue here. This won't occur with a valid form.
    if request.method == "POST":

        # By using the Form.form variable. We can check which form is in use to return the correct error message.
        if type(Form.form) == type(noform):
            if noform.employeeID.data == None:
                employeeData = ""
                departmentData = ""
                selection = "Search an Employee"
                success = ""
                error = "Please Fill in the Required Field"
                return render_template("index.html",form=noform,success=success,employeeData=employeeData,departmentData=departmentData,selection=selection,error=error)
            else:
                employeeData = ""
                departmentData = ""
                selection = "Search an Employee"
                success = ""
                error = "Please enter a valid Employee ID, no numbers equal or less than 0, or Non-Numerical Characters"
                return render_template("index.html",form=noform,success=success,employeeData=employeeData,departmentData=departmentData,selection=selection,error=error)

        # Check which form is in use.
        if type(Form.form) == type(yesform):
            if yesform.employeeName.data == "":
                    employeeData = ""
                    departmentData = ""
                    selection = "Add an Employee"
                    success = ""
                    error = "Please Fill in the Required Field"
                    return render_template("index.html",form=yesform,success=success,employeeData=employeeData,departmentData=departmentData,selection=selection,error=error)

    # An implied Else - If Webpage is obtained via a GET request then it automatically comes here and loads up the base html page.
    return render_template("index.html",form=selectionform,success=success,selection=selection,error=error)


# Nearly Complete
@app.route("/table_mod", methods=["GET","POST"])
def table_mod():

    # Grabbing my forms and other parameters
    selForm = ModSelectForm()
    addForm = AddModForm()
    delForm = DelModForm()
    db = get_db()
    success = ""
    selection = ""

    # Checks AddForm validation, if it passes. It obtains the data
    if  addForm.validate_on_submit():
        tableChoice = addForm.selectionTable.data.lower()
        datatype = addForm.addSelect.data
        columnName = addForm.addMod.data.lower()
        try:
            db.execute("""ALTER TABLE %s ADD %s %s;""" % (tableChoice,columnName,datatype))
            db.commit()
        except:
            success = "There was a SQL error. Please contact IT."
            return render_template("table_mod.html",form=addForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Add a Column")
        if tableChoice == "employee":
            TableColumns.employeeColumns.append(columnName.lower())
        else:
            TableColumns.departmentColumns.append(columnName.lower())
        TableColumns.combinedColumns.append(columnName.lower())
        success = "Column added to table"
        return render_template("table_mod.html",form=addForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Add a Column")
    
    # Checks for DelForm validation, if it passes then it obtains its data.
    if delForm.validate_on_submit():
        tableChoice = delForm.selectionTable.data.lower()
        columnName = delForm.delMod.data.lower()
        if columnName == "name":
            success = "You cannot remove this column."
            return render_template("table_mod.html",form=delForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Remove a Column")
        try:
            db.execute("""ALTER TABLE %s DROP COLUMN %s;""" % (tableChoice,columnName))
            db.commit()
        except:
            success = "There was a SQL error. Please contact IT."
            return render_template("table_mod.html",form=delForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Remove a Column")
            
        if tableChoice == "employee":
            TableColumns.employeeColumns.remove(columnName.lower())
        else:
            TableColumns.departmentColumns.remove(columnName.lower())
        TableColumns.combinedColumns.remove(columnName.lower())
        success = "Column has been removed"
        return render_template("table_mod.html",form=delForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Remove a Column")
    
    # Comes here after the selection has been picked
    if selForm.validate_on_submit():
        modSelect = selForm.selectionMod.data
        if "Add" in modSelect:
            Form.form = addForm
            return render_template("table_mod.html",form=addForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns,selection=modSelect)
        else:
            Form.form = delForm
            return render_template("table_mod.html",form=delForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns,selection=modSelect)
    
    # If None of the forms validated and the method is POST - This implies an invalid form which only occurs on a form page.
    if request.method == "POST":
        if type(Form.form) == type(addForm): 
            success = "Please enter a Column Name"
            return render_template("table_mod.html",form=addForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Add a Column")
        if type(Form.form) == type(delForm): 
            success = "Please enter a Column Name"
            return render_template("table_mod.html",form=delForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection = "Remove a Column")
    
    # If the user arrives at this page with a GET request. Then this triggers and gives back the selection form.
    return render_template("table_mod.html",form=selForm,success=success,tables=TableColumns.tables,employeeColumns=TableColumns.employeeColumns,departmentColumns=TableColumns.departmentColumns, selection=selection)

# In Progress
@app.route("/delete", methods=["GET","POST"])
def delete():
    selform = DelSelectForm()
    employForm = DelEmployForm()
    departForm = DelDepartForm()
    db = get_db()
    selection = ""
    success = ""
    if employForm.validate_on_submit():
        print("Employee Validation")
        removeEmployee = employForm.deleteEmployee.data
        if removeEmployee < 0:
            success = "Error, Please do not use Negative Numbers"
            return render_template("delete.html",form=employForm,success=success,selection="Remove an Employee")
        else:
            db.execute("""DELETE FROM employee WHERE employee_id = ?; """,(removeEmployee,))
            db.commit()
            success = "Employee (Employee ID: %s) removed from Database" %removeEmployee
        return render_template("delete.html",form=employForm,success=success,selection="Remove an Employee")

    if departForm.validate_on_submit():
        print("Department Validation")
        removeDepartment = departForm.deleteDepartment.data.capitalize()
        try:
            removeDepartment = int(removeDepartment)
            db.execute("""DELETE FROM department WHERE department_id = ?;""",(removeDepartment,))
            db.commit()
            success = "Department (ID: %s) Removed from Database" % removeDepartment
        except:
            db.execute("""DELETE FROM department WHERE name = ?;""",(removeDepartment,))
            db.commit()
            success = "Department %s Removed from Database" % removeDepartment
        return render_template("delete.html",form=departForm,success=success,selection="Remove a Department")
    
    if selform.validate_on_submit():
        print("Selection Validation")
        selection = selform.selection.data
        if "Employee" in selection:
            Form.form = employForm
            return render_template("delete.html",form=employForm,success=success,selection=selection)
        else:
            Form.form = departForm
            return render_template("delete.html",form=departForm,success=success,selection=selection)
    
    # If POST method and no forms are validated then this screens for errors
    if request.method == "POST":
        print("No validation")
        if type(Form.form) == type(employForm): 
            success = "Please enter an Employee ID"
            return render_template("delete.html",form=employForm,success=success,selection="Remove an Employee")
        if type(Form.form) == type(departForm): 
            success = "Please enter a Department ID"
            return render_template("delete.html",form=departForm,success=success,selection="Remove a Department")
    
    print("Default")
    return render_template("delete.html",form=selform,success=success,selection=selection)

