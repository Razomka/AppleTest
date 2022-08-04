from flask import Flask, render_template, url_for, request
from database import get_db, close_db
from forms import *


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "THIS-IS-MY-SECRET-KEY"
class Form:
    form = ""

class tableColumns:
    tables = ["employee","department"]
    employeeColumns = ["employee_id - Primary Key - Cannot Be Removed","name","department_id"]
    departmentColumns = ["department_id - Primary Key - Cannot Be Removed","name"]

# Completed and Debugged
@app.route("/", methods=["GET","POST"])
def lookup():
    # A few parameters to get going
    selectionform = selectionForm()
    noform = noForm()
    yesform = yesForm()
    db = get_db()
    selection = ""
    success = ""
    error = ""

    # If the NoForm validates, it comes here
    if noform.validate_on_submit():
        employeeID = noform.employeeID.data
        employeeData = db.execute("""SELECT name,department_id FROM employee WHERE employee_id = ?;""",(employeeID,)).fetchone()
        if employeeData == None:
            success = "There is no employee with this employee ID"
            return render_template("index.html", form=noform, success=success, employeeData=employeeData, departmentData=None, error=error, selection="Search an Employee")
        if employeeData[1] == None:
            employeeData = [employeeData[0],"NULL"]
        departmentData = db.execute("""SELECT name FROM department WHERE department_id = ?;""",(employeeData[1],)).fetchone()
        if departmentData == None:
            departmentData = ["NULL"]
        success = "Success, here is your employee and their department."
        return render_template("index.html", form=noform, success=success, employeeID=employeeID, employeeData=employeeData, departmentData=departmentData, error=error, selection="Search an Employee")
    
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
                return render_template("index.html",form=yesform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData,error=error,selection="Add an Employee")

            db.execute(""" INSERT INTO employee (name,department_id)
                                            VALUES (?,?);""",(employeeName,departmentID))
            db.commit()
            employeeData = db.execute("""SELECT employee_id,name,department_id FROM employee WHERE name = ? AND department_id = ?;""",(employeeName,departmentID)).fetchone()
            employeeID = employeeData[0]
            employeeData = [employeeData[1],employeeData[2]]
            departmentData = db.execute("""SELECT name FROM department WHERE department_id = ?;""",(employeeData[1],)).fetchone()
        
        success = "Success, the employee has been added"
        return render_template("index.html",form=yesform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData,error=error)
    
    # If neither validate then comes here - This only occurs after the selection is posted
    if (selectionform.validate_on_submit()):
        selection = selectionform.selection.data
        if "Search" in selection:
            Form.form = noform
            return render_template("index.html",form=noform,success=success,selection=selection,error=error)    
        else:
            Form.form = yesform
            return render_template("index.html",form=yesform,success=success,selection=selection,error=error)

    if request.method == "POST":
        # Check which form it is and does some validation checks.
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
                error = "Please enter a valid Employee ID, no negative numbers or Non-Numerical Characters"
                return render_template("index.html",form=noform,success=success,employeeData=employeeData,departmentData=departmentData,selection=selection,error=error)

        # Checks which form and does some validation checks. 
        if type(Form.form) == type(yesform):
            if yesform.employeeName.data == "":
                    employeeData = ""
                    departmentData = ""
                    selection = "Add an Employee"
                    success = ""
                    error = "Please Fill in the Required Field"
                    return render_template("index.html",form=yesform,success=success,employeeData=employeeData,departmentData=departmentData,selection=selection,error=error)

    # An implied Else - If Webpage is obtained via a GET request then it automatically comes here and loads up the base html page.
    # selectionBool = False
    return render_template("index.html",form=selectionform,success=success,selection=selection,error=error)


# In Progress
@app.route("/table_mod", methods=["GET","POST"])
def table_mod():
    # Grabbing my forms and other parameters
    selForm = modSelectForm()
    addForm = addModForm()
    delForm = delModForm()
    db = get_db()
    success = ""
    selection = ""

    if  addForm.validate_on_submit():
        print("Addition Form")
        tableChoice = addForm.selectionTable.data.lower()
        datatype = addForm.addSelect.data
        columnName = addForm.addMod.data.lower()
        print(tableChoice)
        print(columnName)
        try:
            db.execute("""ALTER TABLE %s ADD %s %s;""" % (tableChoice,columnName,datatype))
            db.commit()
        except:
            success = "There was a SQL error. Please contact IT."
            return render_template("table_mod.html",form=addForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns, selection = "Add a Column")

        if tableChoice == "employee":
            tableColumns.employeeColumns.append(columnName.lower())
        else:
            tableColumns.departmentColumns.append(columnName.lower())
        success = "Column added to table"
        return render_template("table_mod.html",form=addForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns, selection = "Add a Column")
    
    if delForm.validate_on_submit():
        print("Deletion Form")
        tableChoice = delForm.selectionTable.data.lower()
        columnName = delForm.delMod.data.lower()

        try:
            db.execute("""ALTER TABLE %s DROP COLUMN %s;""" % (tableChoice,columnName))
            db.commit()
        except:
            success = "There was a SQL error. Please contact IT."
            return render_template("table_mod.html",form=delForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns, selection = "Remove a Column")
            
        if tableChoice == "employee":
            tableColumns.employeeColumns.remove(columnName.lower())
        else:
            tableColumns.departmentColumns.remove(columnName.lower())
        success = "Column has been removed"
        return render_template("table_mod.html",form=delForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns, selection = "Remove a Column")
    
    if selForm.validate_on_submit():
        print("Selection Form")
        modSelect = selForm.selectionMod.data
        if "Add" in modSelect:
            return render_template("table_mod.html",form=addForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns,selection=modSelect)
        else:
            return render_template("table_mod.html",form=delForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns,selection=modSelect)
    print("Default")
    return render_template("table_mod.html",form=selForm,success=success,tables=tableColumns.tables,employeeColumns=tableColumns.employeeColumns,departmentColumns=tableColumns.departmentColumns, selection=selection)

@app.route("/delete", methods=["GET","POST"])
def delete():
    form = delSelectForm()
    employForm = delEmployForm()
    departForm = delDepartForm()
    db = get_db()
    success = ""
    return render_template("table_mod.html",form=form,success=success)

