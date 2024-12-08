"""
Form classes for the application.
Contains all WTForms form classes used for data validation and form rendering.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional

class RegisterForm(FlaskForm):
    """
    User registration form.
    
    Fields:
        username: User's desired username
        email: User's email address
        password: User's password
        user_type: Type of user account (student/teacher/staff)
        submit: Form submission button
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('library_staff', 'Library Staff'),('security', 'Security Personnel')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """
    User login form.
    
    Fields:
        email: User's email address
        password: User's password
        submit: Form submission button
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherProfileForm(FlaskForm):
    """
    Teacher profile update form.
    
    Fields:
        school_id: Teacher's school identification number
        name: Teacher's full name
        gender: Teacher's gender selection
        office_location: Teacher's office location
        office_hours: Teacher's office hours
        email: Teacher's contact email
        biography: Teacher's biographical information
        submit: Form submission button
    """
    school_id = StringField('School ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    office_location = StringField('Office Location', validators=[DataRequired()])
    office_hours = StringField('Office Hours', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class StudentProfileForm(FlaskForm):
    """
    Student profile update form.
    
    Fields:
        school_id: Student's school identification number
        name: Student's full name
        gender: Student's gender selection
        birth: Student's birth date
        email: Student's contact email
        college: Student's college/faculty
        major: Student's major/program
        dorm: Student's dormitory information
        biography: Student's biographical information
        submit: Form submission button
    """
    school_id = StringField('School ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    birth = StringField('Birth Date (YYYY-MM-DD)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    college = StringField('College', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    dorm = StringField('Dorm', validators=[DataRequired()])
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class CreateCourseForm(FlaskForm):
    """
    Course creation form.
    
    Fields:
        course_name: Name of the course
        course_code: Unique course identifier
        year: Academic year
        semester: Academic semester
        day_of_week: Day when course is held
        start_period: Starting period number
        end_period: Ending period number
        description: Course description
        submit: Form submission button
    """
    course_name = StringField('Course Name', validators=[DataRequired()])
    course_code = StringField('Course Code', validators=[DataRequired(), Length(min=2, max=20)])
    year = IntegerField('Year', validators=[DataRequired()])
    semester = SelectField('Semester', choices=[('Fall', 'Fall'), ('Spring', 'Spring')], validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], validators=[DataRequired()])
    start_period = IntegerField('Start Period', validators=[DataRequired()])
    end_period = IntegerField('End Period', validators=[DataRequired()])
    description = TextAreaField('Course Description')
    submit = SubmitField('Create Course')

class RegisterCourseForm(FlaskForm):
    """
    Course registration form for students.
    
    Fields:
        course_code: Code of the course to register
        submit: Form submission button
    """
    course_code = StringField('Course Code', validators=[DataRequired()])
    submit = SubmitField('Register Course')

class ForumPostForm(FlaskForm):
    """
    Forum post creation form.
    
    Fields:
        post_title: Title of the post
        post_content: Content of the post
        board_type: Type of forum board (chat/course)
        course_id: Associated course ID (if board_type is 'course')
        submit: Form submission button
    """
    post_title = StringField('Title', validators=[DataRequired()])
    post_content = TextAreaField('Content', validators=[DataRequired()])
    board_type = SelectField('Board Type', choices=[('chat', 'Chat'), ('course', 'Course')], validators=[DataRequired()])
    course_id = IntegerField('Course ID')  # Only required if board_type is 'course'
    submit = SubmitField('Post')

class ForumReplyForm(FlaskForm):
    """
    Forum reply form.
    
    Fields:
        reply_content: Content of the reply
        submit: Form submission button
    """
    reply_content = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')

class LibraryStaffProfileForm(FlaskForm):
    """
    Library staff profile update form.
    
    Fields:
        staff_id: Staff identification number
        name: Staff member's full name
        gender: Staff member's gender
        email: Staff contact email
        department: Library department
        position: Staff position/role
        work_hours: Working hours
        biography: Staff biographical information
        submit: Form submission button
    """
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    work_hours = StringField('Work Hours')
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class SecurityProfileForm(FlaskForm):
    """
    Security staff profile update form.
    
    Fields:
        staff_id: Staff identification number
        name: Staff member's full name
        gender: Staff member's gender
        email: Staff contact email
        shift_hours: Working shift hours
        assigned_area: Assigned security area
        biography: Staff biographical information
        submit: Form submission button
    """
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    shift_hours = StringField('Shift Hours', validators=[DataRequired()])
    assigned_area = StringField('Assigned Area', validators=[DataRequired()])
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class AddBookForm(FlaskForm):
    """
    Library book addition form.
    
    Fields:
        title: Book title
        author: Book author
        publication_year: Year of publication
        category: Book category/genre
        availability_status: Current availability status
        submit: Form submission button
    """
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    publication_year = IntegerField('Publication Year', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('magazine', 'Magazine'),
        ('comic', 'Comic'),
        ('graphic_novel', 'Graphic Novel'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('mystery', 'Mystery'),
        ('fantasy', 'Fantasy'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('self_help', 'Self Help'),
        ('travel', 'Travel'),
        ('health', 'Health'),
        ('cookbook', 'Cookbook'),
        ('poetry', 'Poetry'),
        ('drama', 'Drama'),
        ('adventure', 'Adventure'),
        ('science_fiction', 'Science Fiction'),
        ('technology', 'Technology'),
        ('philosophy', 'Philosophy'),
        ('religion', 'Religion'),
        ('politics', 'Politics'),
        ('art', 'Art'),
        ('music', 'Music'),
        ('sports', 'Sports'),
        ('education', 'Education'),
        ('psychology', 'Psychology'),
        ('law', 'Law'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    availability_status = SelectField('Availability Status', choices=[
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Book')

class SearchBookForm(FlaskForm):
    """
    Library book search form.
    
    Fields:
        title: Book title to search
        author: Book author to search
        publication_year: Publication year to search
        availability_status: Availability status filter
        submit: Form submission button
    """
    title = StringField('Title')
    author = StringField('Author')
    publication_year = IntegerField('Publication Year', 
        validators=[Optional()],  # 只验证是否为整数，不限制范围
        render_kw={"placeholder": "YYYY"})
    availability_status = SelectField('Status', choices=[
        ('', 'All'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')
    ])
    submit = SubmitField('Search')

class AddGradeForm(FlaskForm):
    """
    Student grade addition form.
    
    Fields:
        grade: Letter grade selection
        submit: Form submission button
    """
    grade = SelectField('Grade', choices=[
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D+', 'D+'), ('D', 'D'), ('F', 'F')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Grade')

class EBikeForm(FlaskForm):
    """
    Electric bike registration form.
    
    Fields:
        license_plate: License plate number
        bike_model: E-bike model information
    """
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])
    bike_model = StringField('Bike Model', validators=[DataRequired(), Length(max=50)])

class UserPreferenceForm(FlaskForm):
    """
    User interface preference form.
    
    Fields:
        theme: UI theme selection
        font_size: Font size selection
        submit: Form submission button
    """
    theme = SelectField('Theme', choices=[
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode')
    ], validators=[DataRequired()])
    font_size = SelectField('Font Size', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Preferences')

class EditUserForm(FlaskForm):
    """
    User account edit form.
    
    Fields:
        username: User's username
        email: User's email (readonly)
        password: User's password (optional for change)
        user_type: Type of user account
        submit: Form submission button
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', render_kw={'readonly': True})     
    password = PasswordField('Password (leave blank to keep unchanged)')
    user_type = SelectField('User Type', 
                          choices=[('student', 'Student'),
                                 ('teacher', 'Teacher'),
                                 ('library_staff', 'Library Staff'),
                                 ('security', 'Security'),],
                          validators=[DataRequired()])
    submit = SubmitField('Update User')

class DeleteAccountForm(FlaskForm):
    """
    Account deletion confirmation form.
    
    Fields:
        password: User's password for confirmation
        confirm: Deletion confirmation checkbox
        submit: Form submission button
    """
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    confirm = BooleanField('Confirm Delete', validators=[
        DataRequired(message='You must confirm this action')
    ])
    submit = SubmitField('Delete Account')

    def __init__(self, *args, **kwargs):
        super(DeleteAccountForm, self).__init__(*args, **kwargs)

