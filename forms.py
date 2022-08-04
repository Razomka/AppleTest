from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import InputRequired, NumberRange

# First Drop down menu for Finding or Adding an employee
class SelectionForm(FlaskForm):
    selection = SelectField("Please Choose your Process:",choices=["Search an Employee","Add an Employee"],default="Search An Employee")
    submit = SubmitField("Submit")

# Finding an employee form
class NoForm(FlaskForm):
    employeeID = IntegerField("Please enter the Employees ID (Required)*:",validators=[NumberRange(1,1000)])
    submit = SubmitField("Submit")

# Adding an employee form
class YesForm(FlaskForm):
    employeeName = StringField("Please enter the Employees Name (Required)*:",validators=[InputRequired()])
    departmentID = StringField("Please enter the Department ID (Optional):")
    submit = SubmitField("Submit")

# Drop down menu for Adding or Removing a column 
class ModSelectForm(FlaskForm):
    selectionMod = SelectField("Please Choose Your Process:", choices=["Add a Column","Remove a Column"])
    submit = SubmitField("Submit")

# Form for adding a column
class AddModForm(FlaskForm):
    selectionTable = SelectField("Please Choose Your Table:", choices=["Employee","Department"])
    addSelect = SelectField("Please Pick the Data Type:",choices=["INT","TEXT","DATE"])
    addMod = StringField("Please Enter the New Column Name:",validators=[InputRequired()])
    submit = SubmitField("Submit")

# Form for removing a SQL column
class DelModForm(FlaskForm):
    selectionTable = SelectField("Please Choose Your Table:", choices=["Employee","Department"])
    delMod = StringField("Please Enter the Column Name:",validators=[InputRequired()])
    submit = SubmitField("Submit")

#  Drop down menu for removing an employee or a department
class DelSelectForm(FlaskForm):
    selection = SelectField("Please Choose Your Process:",choices=["Remove an Employee","Remove a Department"])
    submit = SubmitField("Submit")

# Form for removing employee
class DelEmployForm(FlaskForm):
    deleteEmployee = IntegerField("Please enter the Employee ID to Remove:",validators=[InputRequired()])
    submit = SubmitField("Submit")

# Form for removing a department
class DelDepartForm(FlaskForm):
    deleteDepartment = StringField("Please Enter the Department Name or ID to Remove:",validators=[InputRequired()])
    submit = SubmitField("Submit")