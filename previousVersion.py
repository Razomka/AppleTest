from flask import Flask, render_template
from database import get_db, close_db
from flask_session import Session
from forms import *

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "THIS-IS-MY-SECRET-KEY"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET","POST"])
def lookup():
    selectionform = selectionForm()
    noform = noForm()
    yesform = yesForm()
    db = get_db()
    selection = ""
    success = ""
    if noform.validate_on_submit():
        print("I came here to Noform Val")
        employeeID = noform.employeeID.data
        employeeData = db.execute("""SELECT name,department_id FROM employee WHERE employee_id = ?;""",(employeeID,)).fetchone()
        if employeeData[1] == None:
            employeeData = [employeeData[0],"NULL"]
        departmentData = db.execute("""SELECT name FROM department WHERE department_id = ?;""",(employeeData[1],)).fetchone()
        if departmentData == None:
            departmentData = ["NULL"]
        success = "Success, here is your employee and their department."
        return render_template("index.html",form=noform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData)
    if yesform.validate_on_submit():
        print("I came to YesForm Val")
        employeeName = yesform.employeeName.data
        departmentID = yesform.departmentID.data
        if departmentID != None:
            db.execute(""" INSERT INTO employee (name,department_id)
                                            VALUES (?,?);""",(employeeName,departmentID))
            db.commit()
        else:
            db.execute(""" INSERT INTO employee (name) VALUES (?);""",(employeeName))
            db.commit()
        if departmentID != None:
            employeeData = db.execute("""SELECT employee_id,name,department_id FROM employee WHERE name = ? AND department_id = ?;""",(employeeName,departmentID)).fetchone()
            employeeID = employeeData[0]
            employeeData = [employeeData[1],employeeData[2]]
            departmentData = db.execute("""SELECT name FROM department WHERE department_id = ?;""",(employeeData[1],)).fetchone()
        success = "Success, the employee has been added"
        return render_template("index.html",form=yesform,success=success,employeeID=employeeID,employeeData=employeeData,departmentData=departmentData)
    elif selectionform.validate_on_submit():
        print("I came to Selection Form")
        selection = selectionform.selection.data
        if "Search" in selection:
            return render_template("index.html",form=noform,success=success,selection=selection)    
        else:
            return render_template("index.html",form=yesform,success=success,selection=selection)
    return render_template("index.html",form=selectionform,success=success,selection=selection)