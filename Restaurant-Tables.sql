DROP TABLE IF EXISTS Ratings CASCADE;
DROP TABLE IF EXISTS Reservation CASCADE;
DROP TABLE IF EXISTS OrderItems CASCADE;
DROP TABLE IF EXISTS MenuItem CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS Employee CASCADE;
DROP TABLE IF EXISTS Department CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;

CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY,
    fName TEXT,
    lName TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
);

INSERT INTO Customer (customer_id, fName, lName, email, phone, address)
VALUES (1000, 'John', 'Doe', 'john.doe@example.com', '555-1234', '123 Main St');

INSERT INTO Customer (customer_id, fName, lName, email, phone, address)
VALUES (1001, 'Jane', 'Smith', 'jane.smith@example.com', '555-5678', '456 Oak St');

INSERT INTO Customer (customer_id, fName, lName, email, phone, address)
VALUES (1002, 'Bob', 'Johnson', 'bob.johnson@example.com', '555-9876', '789 Pine St');

CREATE TABLE Department (
    dept_name TEXT PRIMARY KEY,
    dept_head INTEGER
);

CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY,
    fName TEXT,
    lName TEXT,
    role TEXT,
    dept_name TEXT,
    FOREIGN KEY (dept_name) REFERENCES Department(dept_name)
);

INSERT INTO Department (dept_name, dept_head) 
VALUES 
('Kitchen', 100), 
('Wait Staff', 200), 
('IT', 300), 
('HR', 400); 

Insert INTO Employee (employee_id, fName, lName, role, dept_name)
VALUES
(100, 'Lincoln', 'Schmidt', 'Head Chef', 'Kitchen'),
(200, 'Alice', 'Vance', 'Wait Staff Manager', 'Wait Staff'),
(300, 'Jodie', 'Davis', 'IT Head', 'IT'),
(400, 'Harry', 'Myers', 'HR Head', 'HR');

ALTER TABLE Department
ADD FOREIGN KEY (dept_head) REFERENCES Employee(employee_id);

CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_datetime timestamp,
    order_type VARCHAR(20) CHECK (order_type IN ('dine-in', 'takeout', 'delivery')),
    total_amount REAL,
    chef_employee_id INTEGER,
    waiter_employee_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (chef_employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (waiter_employee_id) REFERENCES Employee(employee_id)
);

INSERT INTO Orders (order_id, customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id)
VALUES
  (1, 1000, '2023-12-05 12:30:00', 'dine-in', 50.00, 100, 200),
  (2, 1001, '2023-12-05 18:45:00', 'takeout', 35.50, 100, 201),
  (3, 1002, '2023-12-06 19:15:00', 'delivery', 75.20, 101, 200),
  (4, 1000, '2023-12-07 20:00:00', 'dine-in', 60.80, 101, 201),
  (5, 1001, '2023-12-08 15:30:00', 'takeout', 42.90, 101, 200);
 
CREATE TABLE MenuItem (
    menu_item_id INTEGER PRIMARY KEY,
    item_name TEXT,
    description TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE OrderItems (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    menu_item_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (menu_item_id) REFERENCES MenuItem(menu_item_id)
);

CREATE TABLE Reservation (
    reservation_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    reservation_datetime timestamp,
    table_num INTEGER,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Ratings (
    rating_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);


