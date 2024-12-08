"""
Database models for the application.
Contains all SQLAlchemy model classes that represent database tables.
"""

from . import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """
    User model representing all system users.
    
    Attributes:
        id: Primary key
        username: Unique username for the user
        email: User's email address
        password: Hashed password
        user_type: Type of user (student, teacher, etc.)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_banned: User ban status
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_banned = db.Column(db.Boolean, default=False)  # Only keep one ban status field

    def __repr__(self):
        return f'<User {self.username}>'

class TeacherProfile(db.Model):
    """
    Profile information for teachers.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        school_id: Unique school identification number
        name: Teacher's full name
        gender: Teacher's gender
        office_location: Location of teacher's office
        office_hours: Teacher's office hours
        email: Teacher's contact email
        biography: Teacher's biographical information
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    school_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    office_location = db.Column(db.String(100))
    office_hours = db.Column(db.String(50))
    email = db.Column(db.String(120))
    biography = db.Column(db.Text)


class StudentProfile(db.Model):
    """
    Profile information for students.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        school_id: Unique student identification number
        name: Student's full name
        gender: Student's gender
        birth: Student's birth date (YYYY-MM-DD format)
        email: Student's contact email
        college: Student's college/faculty
        major: Student's major/program
        dorm: Student's dormitory information
        biography: Additional student information
        
    Relationships:
        user: One-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    school_id = db.Column(db.String(20), unique=True, nullable=False)  # Unique student ID
    name = db.Column(db.String(100), nullable=False)  # Student name
    gender = db.Column(db.String(10), nullable=True)  # Gender
    birth = db.Column(db.String(10), nullable=True)  # Birth date in "YYYY-MM-DD" format
    email = db.Column(db.String(120), nullable=False)  # Email
    college = db.Column(db.String(100), nullable=True)  # College information
    major = db.Column(db.String(100), nullable=True)  # Major
    dorm = db.Column(db.String(255), nullable=True)  # Dorm information
    biography = db.Column(db.Text, nullable=True)  # Biography field for additional info

    # Define relationship with User
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

class StudentGrade(db.Model):
    """
    Student course grades.
    
    Attributes:
        grade_id: Primary key
        student_id: Foreign key to User model (student)
        course_id: Foreign key to Course model
        grade: Letter grade for the course
        
    Relationships:
        student: Many-to-one relationship with User model
        course: Many-to-one relationship with Course model
    """
    __tablename__ = 'student_grades'

    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)

    # Define relationships to access related models
    student = db.relationship('User', backref='grades', foreign_keys=[student_id])
    course = db.relationship('Course', backref='grades', foreign_keys=[course_id])

    def __repr__(self):
        return f'<StudentGrade {self.grade}>'

class Course(db.Model):
    """
    Course information and schedule.
    
    Attributes:
        id: Primary key
        course_name: Name of the course
        course_code: Unique course identifier
        year: Academic year
        semester: Academic semester
        day_of_week: Day when course is held
        start_period: Starting period number
        end_period: Ending period number
        description: Course description
        created_by: Foreign key to User model (teacher)
        
    Relationships:
        creator: Many-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 建立与 User 模型的关系
    creator = db.relationship('User', backref=db.backref('courses', lazy=True))

class CourseRegistration(db.Model):
    """
    Student course registrations.
    
    Attributes:
        id: Primary key
        course_id: Foreign key to Course model
        user_id: Foreign key to User model (student)
    """
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ForumPost(db.Model):
    """
    Forum posts for course and chat boards.
    
    Attributes:
        post_id: Primary key
        author_id: Foreign key to User model
        post_title: Title of the post
        post_content: Content of the post
        post_date: Post creation timestamp
        board_type: Type of board (chat/course)
        course_id: Foreign key to Course model (optional)
        
    Relationships:
        replies: One-to-many relationship with ForumReply model
        author: Many-to-one relationship with User model
    """
    __tablename__ = 'forum_post'
    post_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_title = db.Column(db.String(255), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, default=datetime.utcnow)
    board_type = db.Column(db.String(20), nullable=False)  # "chat" or "course"
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)

    # Cascade delete replies when a post is deleted
    replies = db.relationship('ForumReply', cascade="all, delete-orphan", backref='post')
    # Define the relationship to access the User model
    author = db.relationship('User', backref='posts')

class ForumReply(db.Model):
    """
    Replies to forum posts.
    
    Attributes:
        reply_id: Primary key
        post_id: Foreign key to ForumPost model
        replier_id: Foreign key to User model
        reply_content: Content of the reply
        reply_date: Reply creation timestamp
        
    Relationships:
        replier: Many-to-one relationship with User model
    """
    __tablename__ = 'forum_reply'
    reply_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.post_id'), nullable=False)
    replier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reply_content = db.Column(db.Text, nullable=False)
    reply_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Define the relationship to access the User model
    replier = db.relationship('User', backref='replies')

class LibraryStaffProfile(db.Model):
    """
    Profile information for library staff.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        staff_id: Unique staff identification number
        name: Staff member's full name
        gender: Staff member's gender
        email: Staff contact email
        department: Library department
        position: Staff position/role
        work_hours: Working hours
        biography: Staff biographical information
        
    Relationships:
        user: One-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)  # 图书馆部门
    position = db.Column(db.String(100), nullable=False)    # 职位
    work_hours = db.Column(db.String(100))                 # 工作时间
    biography = db.Column(db.Text, nullable=True)

    # Define relationship with User
    user = db.relationship('User', backref=db.backref('library_staff_profile', uselist=False))

class SecurityProfile(db.Model):
    """
    Profile information for security staff.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        staff_id: Unique staff identification number
        name: Staff member's full name
        gender: Staff member's gender
        email: Staff contact email
        shift_hours: Working shift hours
        assigned_area: Assigned security area
        biography: Staff biographical information
        
    Relationships:
        user: One-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(120), nullable=False)
    shift_hours = db.Column(db.String(100), nullable=False)
    assigned_area = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('security_profile', uselist=False))


class LibraryResource(db.Model):
    """
    Library resources and materials.
    
    Attributes:
        resource_id: Primary key
        title: Resource title
        author: Resource author
        publication_year: Year of publication
        availability_status: Current status (available/borrowed/etc.)
        category: Resource category
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = 'library_resources'
    
    resource_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    availability_status = db.Column(db.String(20), nullable=False, default='available')
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LibraryResource {self.title}>'

class EBikeLicense(db.Model):
    """
    Electric bike registration and licenses.
    
    Attributes:
        license_id: Primary key
        owner_id: Foreign key to User model
        license_plate: License plate number
        bike_model: E-bike model information
        registration_date: Date of registration
        expiration_date: License expiration date
        approved_by: Foreign key to User model (approver)
        status: License status (Pending/Approved/Expired/etc.)
        
    Relationships:
        owner: Many-to-one relationship with User model
        approver: Many-to-one relationship with User model
    """
    __tablename__ = 'e_bike_license'

    license_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    bike_model = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Enum('Pending', 'Approved', 'Expired', "Rejected", "Cancelled"), default='Pending')

    owner = db.relationship('User', foreign_keys=[owner_id])
    approver = db.relationship('User', foreign_keys=[approved_by])


class AdminProfile(db.Model):
    """
    Profile information for system administrators.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        staff_id: Unique staff identification number
        name: Administrator's full name
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class UserPreference(db.Model):
    """
    User interface preferences.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        theme: UI theme preference (light/dark/blue)
        font_size: Font size preference (small/medium/large)
        created_at: Preference creation timestamp
        updated_at: Last update timestamp
        
    Relationships:
        user: One-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')  # light, dark, blue
    font_size = db.Column(db.String(10), default='medium')  # small, medium, large
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('preference', uselist=False))

class ChatHistory(db.Model):
    """
    User chat history with AI assistant.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        message: User's message
        response: AI assistant's response
        created_at: Chat timestamp
        
    Relationships:
        user: Many-to-one relationship with User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='chat_history')
