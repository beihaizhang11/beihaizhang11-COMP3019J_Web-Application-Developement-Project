# COMP3019J Project

English | [简体中文](README_zh.md)
### Project Name: BJUT Unified Identity Authentication System

### Team_20 Members:

* Bohan Zhang 22207251
* Yunhan Gao 22207250
* Le Liu 22207256

### Project Description

The primary goal of this project is to design and implement a comprehensive university website that offers a personalized and functional experience for different types of users. The website provides students, teachers, library staff and other security personnel with an interface to manage their profiles, interact with others, and access university resources based on their roles.

### Core Features
1. Unified Authentication
2. Course Management System
3. Library Management System
4. E-bike Registration System
5. Forum Platform
6. Theme Customization
7. AI Assistant
8. System Logging

### Preview this project

This is a **preview version** of this project. Please use Python to run this project locally to see the latest website.

[http://webappdev.zhangbh.com/](http://webappdev.zhangbh.com/)

### Run this project

#### Set up environment

1. Install Python 3.10
2. Using the following code to set up the environment:

```shell
python -V                 # Print out python version for debugging
pip install virtualenv
virtualenv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
```

#### Run this web server

```shell
flask run
```

or

```shell
python run.py
````

#### Access the website

URL: http://localhost:5000 or http://127.0.0.1:5000

### Characteristics

* Role-based access control
* CSRF Protection
* Blueprint architecture
* Password encryption
* Comprehensive logging system
* Theme customization (Light/Dark mode)
* ![image](Project%20Document/STYLE.gif)
* Form validation with JavaScript
* ![image](Project%20Document/JS.gif)
* AJAX for dynamic updates  
* ![image](Project%20Document/AJAX_S.gif)
* ![image](Project%20Document/AJAX_T.gif)
* AI Assistant
* ![image](Project%20Document/AI.gif)

### Roles in the System

1. System Administrator
   - User Management: Add, edit, and delete user accounts
   - System Configuration: Manage website settings
   - Log monitoring and system maintenance
   - Access to all system features
   - AI Assistant

2. Student
   - Course Management: View and register for courses
   - Grade Viewing: Check personal academic performance
   - Library Access: Search books and view borrowing history
   - E-bike Registration: Register personal e-bikes
   - Forum Participation: Engage in discussions
   - Profile Management: Update personal information
   - Theme Customization: Modify interface appearance
   - AI Assistant

3. Teacher
   - Course Management: Create and manage courses
   - Student Management: Handle course enrollments
   - Grade Management: Input and update grades
   - Library Access: Search and borrow resources
   - Forum Participation: Create and moderate discussions
   - Profile Management: Update personal information
   - Theme Customization: Modify interface appearance
   - AI Assistant

4. Library Staff
   - Resource Management: Manage library inventory
   - Loan Record Management: Handle borrowing records
   - Profile Management: Update personal information
   - Theme Customization: Modify interface appearance
   - AI Assistant

5. Security Personnel
   - E-bike Registration Approval: Review student applications
   - Profile Management: Update personal information
   - Theme Customization: Modify interface appearance
   - AI Assistant

6. Visitor
   - Library Catalog Browsing: Search available resources
   - Contact Information Access: View department details

### Technical Details

* Backend Framework: Python Flask
* Database: MySQL with SQLAlchemy ORM
* Frontend: 
  - HTML5 & CSS3
  - JavaScript for dynamic interactions
* Authentication: Flask-Login
* Form Handling: Flask-WTF
* Security Features:
  - CSRF Protection
  - Password Hashing
  - Session Management
  - Role-based Access Control

### Project Structure

```shell
app/
├── api/
├── static/        # Static resources (CSS, JS, images)
├── templates/     # HTML templates
├── utils/         # Utility functions
├── routes.py/     # Route controllers
├── models.py/     # Database models
└── forms.py/      # Form classes
```

### Test Accounts

| Role          | Username                  | Password |
|---------------|---------------------------|----------|
| Admin         | le.liu@emails.bjut.edu.cn | 123      |
| Student       | bohan.zhang@ucdconnect.ie | 20040422 |
| Teacher       | 2742707462@qq.com         | 20040422 |
| Library Staff | gaoyunhan0@gmail.com      | 123456   |
| Security      | mty@gmail.com             | 20040422 |

### Future Development Plans

1. Enhanced User Experience
   - Improved UI/UX design
   - Mobile responsiveness optimization
   - Real-time notifications

2. Advanced Features
   - Advanced role-based access control
   - API integration capabilities
   - Mobile application development
   - Performance optimization
   - Enhanced security measures

3. System Expansion
   - Additional user roles
   - More customization options
   - Integration with other university systems

### File and Directory Structure

```shell
web-application/
├── app/                 # Detailed go to Project Structure
├── logs/                # Website logs for admin
├── Project Document/    # Project document and videos
├── tests/               # Tests
├── .env/                # Enviroment variables
├── .env.example/        # Example for environment variables
├── .gitignore/ 
├── config.py/           # Config files
├── README.md/
├── requirements.txt/
└── run.py/
```

### Contact Information

For any questions or suggestions, please contact:
Email: beihaizhang11@gmail.com
Address: 100 Pingleyuan, Chaoyang District, Beijing

### Repository

Repository URL: https://csgitlab.ucd.ie/webApplication/web-application

### License

MIT License

Copyright (c) 2024 Team 20 Bohan Zhang, Yunhan Gao and Le Liu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.