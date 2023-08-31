-- create a database by click on create a new schema on MySql workbench
CREATE SCHEMA sw_companydb;
use sw_companydb;

-- craete users table. This table will store user login and signup information.
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- create user profile table. This table will store user profile information.
CREATE TABLE UserProfile (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);



-- create course table. This table will store information about the courses offered.
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    details TEXT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- craete purchase table. This table will store information about the courses offered.
CREATE TABLE Purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    item_type ENUM('course', 'project', 'internship') NOT NULL,
    purchase_date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (item_id) REFERENCES Courses(course_id)
);

-- create project table. This table will store information about the projects available for sale.
CREATE TABLE Projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    details TEXT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- create internship table. This table will store internship details related to users.
CREATE TABLE Internship (
    internship_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- some basic commands for showing how it looks like.
show tables;
desc users;
desc UserProfile;
desc Courses;
desc Projects;
desc Internship;
desc Purchases;

-- Some Example for adding data. It depends upon us to customize it. It is just for uderstading
-- Insert user data
INSERT INTO Users (email, password) VALUES ('user@example.com', 'hashed_password');

-- Get the last inserted user_id
SET @last_user_id = LAST_INSERT_ID();

-- Insert user profile data
INSERT INTO UserProfile (user_id, full_name, address, phone) VALUES (@last_user_id, 'John Doe', '123 Main St', '123-456-7890');

