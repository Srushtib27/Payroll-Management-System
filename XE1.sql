
CREATE TABLE users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE,
    password VARCHAR2(200),
    role VARCHAR2(20)
);

CREATE TABLE employee (
    employeeid NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    department VARCHAR2(50),
    salary NUMBER
);


INSERT INTO users VALUES (1, 'emp1', '<HASH_HERE>', 'employee');
INSERT INTO users VALUES (2, 'hr1', '<HASH_HERE>', 'hr');
INSERT INTO users VALUES (3, 'fin1', '<HASH_HERE>', 'finance');

INSERT INTO employee VALUES (1, 'Employee One', 'Sales', 45000);
INSERT INTO employee VALUES (2, 'HR Head', 'Human Resources', 60000);
INSERT INTO employee VALUES (3, 'Finance Manager', 'Finance', 70000);

COMMIT;

CREATE OR REPLACE PACKAGE payroll_pkg AS
    PROCEDURE calculate_salary(p_emp_id NUMBER);
END payroll_pkg;
/

CREATE OR REPLACE PACKAGE BODY payroll_pkg AS
    PROCEDURE calculate_salary(p_emp_id NUMBER) IS
    BEGIN
        UPDATE employee
        SET salary = salary + 1000
        WHERE employeeid = p_emp_id;
    END;
END payroll_pkg;
/

    
