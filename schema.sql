DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS department;

create TABLE employee
(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE department
(
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL
);

INSERT INTO employee values
(001,'John',100),
(002,'Jane',200),
(003,'Jill', NULL);

INSERT INTO department VALUES
(100, 'Finance'),
(101, 'Engineering');