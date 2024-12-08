from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import SQLAlchemyError  # 添加这行
from app.forms import RegisterForm, LoginForm, TeacherProfileForm, StudentProfileForm, CreateCourseForm, \
    RegisterCourseForm, ForumPostForm, ForumReplyForm, LibraryStaffProfileForm, AddBookForm, SearchBookForm, \
    AddGradeForm, EBikeForm, SecurityProfileForm, UserPreferenceForm, EditUserForm, DeleteAccountForm
from app.models import User, TeacherProfile, StudentProfile, Course, CourseRegistration, db, ForumPost, ForumReply, \
    LibraryStaffProfile, LibraryResource, StudentGrade, EBikeLicense, SecurityProfile, AdminProfile, UserPreference, \
    ChatHistory
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.logger import SystemLogger
import os
import requests
import json
import time

main_routes = Blueprint('main', __name__)
system_logger = SystemLogger()

@main_routes.before_request
def check_banned():
    """Check if current user is banned before each request.

    Returns:
        - If banned: Logout and redirect to index with ban message
        - If not banned: None (continue request)

    Logging:
        - None
    """
    # 检查当前用户是否登录且被封禁
    if current_user.is_authenticated and current_user.is_banned:
        # 如果是被封禁用户,则登出并重定向到首页
        logout_user()
        flash('Your account has been banned. Please contact the administrator.','danger')
        return redirect(url_for('main.index'))



@main_routes.route('/', methods=['GET', 'POST'])
def index():
    """Handle user login and homepage.

    Methods:
        GET: Display login form
        POST: Process login attempt

    Returns:
        - If authenticated: Redirect to user profile
        - If login fails: Render index with error message
        - If banned: Redirect to index with ban message

    Logging:
        - INFO: Successful login
        - WARNING: Failed login attempts, banned user attempts
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.profile', user_id=current_user.id))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.is_banned:
                system_logger.log_warning(f"Banned user attempted to login: {user.username}")
                flash('Your account has been banned.', 'danger')
                return redirect(url_for('main.index'))
            
            login_user(user)
            system_logger.log_info(f"User logged in successfully: {user.username}")
            return redirect(url_for('main.profile', user_id=user.id))
        else:
            system_logger.log_warning(f"Failed login attempt for email: {form.email.data}")
            # 修改这里：添加表单错误而不是使用 flash
            if user:
                form.password.errors.append('Incorrect password')
            else:
                form.email.errors.append('Email not found')
            return render_template('index.html', form=form)
    
    return render_template('index.html', form=form)

@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration.

    Methods:
        GET: Display registration form
        POST: Process registration attempt

    Returns:
        GET: Render register.html with form
        POST: 
            - Success: Redirect to index
            - Failure: Redirect back to register with error

    Validation:
        - Checks for existing email
        - Hashes password before storage
    """
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('This email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('main.register'))

        # Create a new user
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.user_type.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)

@main_routes.route('/logout')
@login_required
def logout():
    """Handle user logout.

    Returns:
        Redirect to index page with logout message

    Permission:
        - Requires user to be logged in
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@main_routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    """Display user profile based on user type.

    Args:
        user_id (int): The ID of the user to display

    Returns:
        Renders different dashboard templates based on user_type:
        - student: student_dashboard.html with courses and timetable
        - teacher: teacher_dashboard.html with courses
        - library_staff: library_staff_dashboard.html
    """
    user = User.query.get_or_404(user_id)

    # Check if the user is a student
    if user.user_type == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        registrations = CourseRegistration.query.filter_by(user_id=user.id).all()
        courses = [Course.query.get(reg.course_id) for reg in registrations]

        # Generate a timetable for the student
        timetable = [['' for _ in range(5)] for _ in range(12)]
        for course in courses:
            day_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].index(course.day_of_week)
            for period in range(course.start_period - 1, course.end_period):
                timetable[period][day_index] = course.course_name

        return render_template(
            'student_dashboard.html',
            user=user,
            student=profile,
            courses=courses,
            timetable=timetable
        )

    # Check if the user is a teacher
    elif user.user_type == 'teacher':
        profile = TeacherProfile.query.filter_by(user_id=user.id).first()
        form = TeacherProfileForm(obj=profile)

        # Get courses created by the teacher
        courses = Course.query.filter_by(created_by=user.id).all()

        return render_template(
            'teacher_dashboard.html',
            user=user,
            profile=profile,  # Pass profile data to the template
            courses=courses
        )

    # Check if the user is a library_staff
    elif user.user_type == 'library_staff':
        profile = LibraryStaffProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'library_staff_dashboard.html',
            user=user,
            profile=profile
        )
    
    # Check if the user is a security personnel
    elif user.user_type == 'security':
        profile = SecurityProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'security_dashboard.html',
            user=user,
            profile=profile
        )
    
    elif user.user_type == 'admin':
        profile = AdminProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'admin_dashboard.html',
            user=user,
            profile=profile
        )

    # If user_type is not recognized, return an error
    flash("Invalid user type.", "danger")
    return redirect(url_for('main.profile', user_id=user_id))

@main_routes.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    """Handle user profile editing.

    Args:
        user_id (int): The ID of the user whose profile is being edited

    Methods:
        GET: Display profile edit form
        POST: Process profile updates

    Returns:
        GET: Render appropriate edit form based on user type
        POST: Redirect to profile page after successful update

    Permission:
        - Users can only edit their own profiles
        - Redirects if attempting to edit other users' profiles

    Raises:
        404: If user_id not found
    """
    user = User.query.get_or_404(user_id)

    # Ensure only the current user can edit their profile
    if user.id != current_user.id:
        flash("You are not authorized to edit this profile.", "danger")
        return redirect(url_for('main.profile', user_id=user_id))

    # Handle student profile editing
    if user.user_type == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        form = StudentProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = StudentProfile(user_id=user.id)
            profile.school_id = form.school_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.birth = form.birth.data
            profile.email = form.email.data
            profile.college = form.college.data
            profile.major = form.major.data
            profile.dorm = form.dorm.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))

        return render_template('edit_profile.html', form=form, user=user)

    # Handle teacher profile editing
    elif user.user_type == 'teacher':
        profile = TeacherProfile.query.filter_by(user_id=user.id).first()
        form = TeacherProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = TeacherProfile(user_id=user.id)
            profile.school_id = form.school_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.office_location = form.office_location.data
            profile.office_hours = form.office_hours.data
            profile.email = form.email.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))

        return render_template('edit_profile.html', form=form, user=user)

    # Check if the user is a library_staff
    elif user.user_type == 'library_staff':
        profile = LibraryStaffProfile.query.filter_by(user_id=user.id).first()
        form = LibraryStaffProfileForm(obj=profile)
        
        if form.validate_on_submit():
            if not profile:
                profile = LibraryStaffProfile(user_id=user.id)
            profile.staff_id = form.staff_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.email = form.email.data
            profile.department = form.department.data
            profile.position = form.position.data
            profile.work_hours = form.work_hours.data
            profile.biography = form.biography.data
            
            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
            
        return render_template('edit_profile.html', form=form, user=user)
    
    # Handle security personnel profile editing
    elif user.user_type == 'security':
        profile = SecurityProfile.query.filter_by(user_id=user.id).first()
        form = SecurityProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = SecurityProfile(user_id=user.id)
            profile.staff_id = form.staff_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.shift_hours = form.shift_hours.data
            profile.assigned_area = form.assigned_area.data
            profile.email = form.email.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
        
        return render_template('edit_profile.html', form=form, user=user)

    flash("Invalid user type.", "danger")
    return redirect(url_for('main.profile', user_id=user_id))

@main_routes.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    """Create a new course.

    Methods:
        GET: Display course creation form
        POST: Process new course submission

    Returns:
        GET: Render create_course.html with form
        POST: Redirect to course listing after successful creation

    Permission:
        - Requires teacher privileges

    Validation:
        - Checks for schedule conflicts
        - Validates course capacity
        - Verifies room availability

    Logging:
        - INFO: Course creation success
        - ERROR: Creation failures
    """
    if current_user.user_type != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('main.index'))
    form = CreateCourseForm()
    if form.validate_on_submit():
        new_course = Course(
            course_name=form.course_name.data,
            course_code=form.course_code.data,
            year=form.year.data,
            semester=form.semester.data,
            day_of_week=form.day_of_week.data,
            start_period=form.start_period.data,
            end_period=form.end_period.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    return render_template('create_event.html', form=form)

@main_routes.route('/register_course', methods=['GET', 'POST'])
@login_required
def register_course():
    """Register a student for a course.

    Returns:
        GET: Render registration form with teacher list
        POST: Process course registration
    """
    if current_user.user_type != 'student':
        flash('Only students can register for courses.', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegisterCourseForm()
    
    # 获取所有教师用户
    teachers = User.query.filter_by(user_type='teacher').all()
    
    if form.validate_on_submit():
        course = Course.query.filter_by(course_code=form.course_code.data).first()
        if not course:
            flash('Course not found. Please check the course code.', 'danger')
            return redirect(url_for('main.register_course'))
            
        existing_registration = CourseRegistration.query.filter_by(
            course_id=course.id, 
            user_id=current_user.id
        ).first()
        
        if existing_registration:
            flash('You are already registered for this course.', 'danger')
            return redirect(url_for('main.register_course'))
            
        new_registration = CourseRegistration(
            course_id=course.id, 
            user_id=current_user.id
        )
        db.session.add(new_registration)
        db.session.commit()
        
        flash('Course registered successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
        
    return render_template('register_event.html', form=form, teachers=teachers)

@main_routes.route('/get_teacher_courses/<int:teacher_id>')
@login_required
def get_teacher_courses(teacher_id):
    """Get courses created by a specific teacher.
    
    Args:
        teacher_id (int): ID of the teacher
        
    Returns:
        JSON response with courses list
    """
    if current_user.user_type != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        courses = Course.query.filter_by(created_by=teacher_id).all()
        courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'course_code': course.course_code,
            'semester': course.semester
        } for course in courses]
        
        return jsonify({
            'status': 'success',
            'courses': courses_data
        })
        
    except Exception as e:
        system_logger.log_error(f"Error fetching teacher courses: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch courses'
        }), 500

@main_routes.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit existing course information.

    Args:
        course_id (int): ID of the course to edit

    Methods:
        GET: Display course edit form
        POST: Process course information updates

    Returns:
        GET: Render edit_course.html with form
        POST: Redirect to course listing after successful update

    Permission:
        - Requires teacher privileges

    Logging:
        - INFO: Course update success
        - ERROR: Update failures
    """
    if current_user.user_type != 'teacher':
        flash('Only teachers can edit courses.', 'danger')
        return redirect(url_for('main.index'))
    course = Course.query.get_or_404(course_id)
    form = CreateCourseForm(obj=course)
    if form.validate_on_submit():
        course.course_name = form.course_name.data
        course.course_code = form.course_code.data
        course.year = form.year.data
        course.semester = form.semester.data
        course.day_of_week = form.day_of_week.data
        course.start_period = form.start_period.data
        course.end_period = form.end_period.data
        course.description = form.description.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    return render_template('edit_course.html', form=form, course=course)

@main_routes.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete a course and all related data.

    Args:
        course_id (int): The ID of the course to delete

    Returns:
        POST: Redirect to manage_courses page

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Actions:
        - Deletes course grades
        - Deletes course registrations
        - Deletes forum posts and replies
        - Deletes course itself

    Logging:
        - INFO: Course deletion success
        - ERROR: Deletion failures
    """
    if current_user.user_type != 'teacher':
        flash('Only teachers can delete courses.', 'danger')
        return redirect(url_for('main.index'))
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('main.profile', user_id=current_user.id))

@main_routes.route('/forum/<string:board_type>')
@login_required
def forum(board_type):
    """
    Display forum posts based on board type and user role.

    Args:
        board_type (str): Type of forum board ('chat' or 'course')

    Returns:
        Rendered forum.html template with filtered posts

    Access Control:
        - Requires authentication
        - Limited to students and teachers
        - Students can only see posts from their registered courses
        - Teachers can see all course posts

    Board Types:
        - chat: General discussion board accessible to all authorized users
        - course: Course-specific discussion board with restricted access

    Error Handling:
        - Redirects to index with error message for unauthorized access
        - Redirects to index with error message for invalid board type
    """
    # Ensure only students and teachers can access
    if current_user.user_type not in ['student', 'teacher']:
        flash("You are not authorized to access this board.", "danger")
        return redirect(url_for('main.index'))

    # Validate board type
    if board_type not in ['chat', 'course']:
        flash("Invalid board type.", "danger")
        return redirect(url_for('main.index'))

    if board_type == "course":
        if current_user.user_type == "student":
            # Get courses the student is registered for
            registrations = CourseRegistration.query.filter_by(user_id=current_user.id).all()
            course_ids = [reg.course_id for reg in registrations]
            posts = ForumPost.query.filter(
                ForumPost.board_type == "course", 
                ForumPost.course_id.in_(course_ids)
            ).all()
        else:
            # Teachers can see all course posts
            posts = ForumPost.query.filter_by(board_type="course").all()
    else:
        # Chat board shows all general discussion posts
        posts = ForumPost.query.filter_by(board_type="chat").all()

    return render_template('forum.html', posts=posts, board_type=board_type)

@main_routes.route('/forum/<string:board_type>/create', methods=['GET', 'POST'])
@login_required
def create_post(board_type):
    """Create a new forum post.

    Args:
        board_type (str): Type of forum board ('course' or 'general')

    Methods:
        GET: Display post creation form
        POST: Process new post submission

    Returns:
        GET: Render create_post.html with form
        POST: Redirect to forum board after successful creation

    Permission:
        - Requires user to be logged in
        - Course forums require course enrollment

    Logging:
        - INFO: Post creation success
    """
    form = ForumPostForm(board_type=board_type)  # Set the board type in the form

    if form.validate_on_submit():
        new_post = ForumPost(
            author_id=current_user.id,
            post_title=form.post_title.data,
            post_content=form.post_content.data,
            board_type=board_type,  # Directly from URL param
            course_id=form.course_id.data if board_type == "course" else None
        )
        db.session.add(new_post)
        db.session.commit()
        system_logger.log_info(f"User {current_user.username} created a new post in {board_type} board")
        flash("Post created successfully!", "success")
        return redirect(url_for('main.forum', board_type=board_type))
    return render_template('create_post.html', form=form, board_type=board_type)

@main_routes.route('/forum/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    """
    View a forum post and handle replies.

    Args:
        post_id (int): ID of the forum post to view

    Methods:
        GET: Display post and existing replies
        POST: Process new reply submission

    Returns:
        GET: Rendered view_post.html with post, replies, and reply form
        POST: Redirect back to post page after successful reply

    Access Control:
        - Requires authentication
        - All authenticated users can view posts and add replies

    Error Handling:
        - Returns 404 if post not found
        - Form validation for reply submission

    Database Operations:
        - Reads post and replies from database
        - Creates new reply records on POST
    """
    post = ForumPost.query.get_or_404(post_id)
    form = ForumReplyForm()
    
    if form.validate_on_submit():
        new_reply = ForumReply(
            post_id=post_id,
            replier_id=current_user.id,
            reply_content=form.reply_content.data
        )
        db.session.add(new_reply)
        db.session.commit()
        flash("Reply posted successfully!", "success")
        return redirect(url_for('main.view_post', post_id=post_id))

    replies = ForumReply.query.filter_by(post_id=post_id).all()
    return render_template('view_post.html', 
                         post=post, 
                         replies=replies, 
                         form=form)

@main_routes.route('/forum/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Delete a forum post and all associated replies.

    Args:
        post_id (int): ID of the post to delete

    Methods:
        POST: Process post deletion request

    Returns:
        Redirect to forum board after deletion

    Access Control:
        - Requires authentication
        - Only post author can delete their own posts

    Error Handling:
        - Returns 404 if post not found
        - Redirects with error message if user is not post author

    Database Operations:
        - Deletes post and cascades to associated replies
        - Commits transaction
    """
    post = ForumPost.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash("You can only delete your own posts.", "danger")
        return redirect(url_for('main.forum', board_type=post.board_type))

    db.session.delete(post)
    db.session.commit()
    flash("Post and its replies have been deleted.", "success")
    return redirect(url_for('main.forum', board_type=post.board_type))

@main_routes.route('/forum/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(reply_id):
    """
    Delete a forum reply.

    Args:
        reply_id (int): ID of the reply to delete

    Methods:
        POST: Process reply deletion request

    Returns:
        Redirect to original post page after deletion

    Access Control:
        - Requires authentication
        - Only reply author can delete their own replies

    Error Handling:
        - Returns 404 if reply not found
        - Redirects with error message if user is not reply author

    Database Operations:
        - Deletes single reply
        - Commits transaction
    """
    reply = ForumReply.query.get_or_404(reply_id)
    if reply.replier_id != current_user.id:
        flash("You can only delete your own replies.", "danger")
        return redirect(url_for('main.view_post', post_id=reply.post_id))

    db.session.delete(reply)
    db.session.commit()
    flash("Reply has been deleted.", "success")
    return redirect(url_for('main.view_post', post_id=reply.post_id))

@main_routes.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add a new book to the library system.

    Methods:
        GET: Display book addition form
        POST: Process new book submission

    Returns:
        GET: Render add_book.html with form
        POST: Redirect to library dashboard after successful addition

    Permission:
        - Requires library_staff privileges

    Logging:
        - INFO: Book addition success
        - ERROR: Addition failures
    """
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        try:
            new_book = LibraryResource(
                title=form.title.data,
                author=form.author.data,
                publication_year=form.publication_year.data,
                category=form.category.data,
                availability_status=form.availability_status.data
            )
            db.session.add(new_book)
            db.session.commit()
            flash('New book added successfully!', 'success')
            return redirect(url_for('main.manage_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')
            return redirect(url_for('main.add_book'))
    
    return render_template('add_book.html', form=form)

@main_routes.route('/search_books', methods=['GET', 'POST'])
def search_books():
    """Handle book search functionality.
    
    Methods:
        GET: Display search form
        POST: Process search and display results
        
    Returns:
        Rendered template with search form and results
        
    Access:
        - Public access allowed
        - Supports both authenticated and guest users
    """
    form = SearchBookForm()
    query = LibraryResource.query
    
    if form.validate_on_submit():
        if form.title.data:
            query = query.filter(LibraryResource.title.ilike(f'%{form.title.data}%'))
        if form.author.data:
            query = query.filter(LibraryResource.author.ilike(f'%{form.author.data}%'))
        if form.publication_year.data:
            query = query.filter(LibraryResource.publication_year == form.publication_year.data)
        if form.availability_status.data:
            query = query.filter(LibraryResource.availability_status == form.availability_status.data)
    
    books = query.all()
    book_count = len(books)
    
    # 添加搜索结果提示
    if form.validate_on_submit():  # 只在提交搜索时显示提示
        if book_count == 0:
            flash('No books found matching your search criteria.', 'info')
        elif book_count == 1:
            flash('Successfully found 1 book!', 'success')
        else:
            flash(f'Successfully found {book_count} books!', 'success')
    
    # 添加一个标志来标识是否是访客访问
    is_guest = not current_user.is_authenticated
    
    return render_template('search_books.html', 
                         form=form, 
                         books=books,
                         is_guest=is_guest)  # 传递访客标志到模板

@main_routes.route('/library_statistics')
@login_required
def library_statistics():
    """
    Display library statistics for library staff.

    Access Control:
        - Requires library_staff privileges

    Returns:
        Rendered template with library statistics data
    """
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    # 取基本统计数据
    total_books = LibraryResource.query.count()
    available_books = LibraryResource.query.filter_by(availability_status='available').count()
    borrowed_books = LibraryResource.query.filter_by(availability_status='borrowed').count()
    reserved_books = LibraryResource.query.filter_by(availability_status='reserved').count()
    
    # 获取分类统计
    category_stats = db.session.query(
        LibraryResource.category, 
        db.func.count(LibraryResource.resource_id)
    ).group_by(LibraryResource.category).all()
    
    return render_template('library_statistics.html',
                         total_books=total_books,
                         available_books=available_books,
                         borrowed_books=borrowed_books,
                         reserved_books=reserved_books,
                         category_stats=category_stats)

@main_routes.route('/manage_books', methods=['GET', 'POST'])
@login_required
def manage_books():
    """
    Display book management interface for library staff.

    Methods:
        GET: Display book management page
        POST: Process book search and display results

    Access Control:
        - Requires library_staff privileges

    Returns:
        Rendered template with book management data
    """
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        form = SearchBookForm()
        query = LibraryResource.query
        
        if form.validate_on_submit():
            if form.title.data:
                query = query.filter(LibraryResource.title.ilike(f'%{form.title.data}%'))
            if form.author.data:
                query = query.filter(LibraryResource.author.ilike(f'%{form.author.data}%'))
            if form.publication_year.data:
                query = query.filter(LibraryResource.publication_year == form.publication_year.data)
            if form.availability_status.data:
                query = query.filter(LibraryResource.availability_status == form.availability_status.data)
        
        books = query.all()
        book_count = len(books)
        
        # 添加搜索结果提示
        if form.validate_on_submit():
            if book_count == 0:
                flash('No books found matching your search criteria.', 'info')
            elif book_count == 1:
                flash('Successfully found 1 book!', 'success')
            else:
                flash(f'Successfully found {book_count} books!', 'success')
        
        return render_template('manage_books.html', 
                             books=books,
                             form=form)
                             
    except Exception as e:
        system_logger.log_error(f"Error in manage_books: {str(e)}")
        flash('An error occurred while loading the books.', 'danger')
        return redirect(url_for('main.index'))

@main_routes.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    """Edit existing book information.

    Args:
        book_id (int): ID of the book to edit

    Methods:
        GET: Display book edit form
        POST: Process book information updates

    Returns:
        GET: Render edit_book.html with form
        POST: Redirect to library dashboard after successful update

    Permission:
        - Requires library_staff privileges

    Logging:
        - INFO: Book update success
        - ERROR: Update failures
    """
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    book = LibraryResource.query.get_or_404(book_id)
    form = AddBookForm(obj=book)
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.publication_year = form.publication_year.data
        book.category = form.category.data
        book.availability_status = form.availability_status.data  # 更新借阅状态
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('main.manage_books'))
    
    return render_template('edit_book.html', form=form, book=book)

@main_routes.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    """
    Delete a book from the library.

    Args:
        book_id (int): ID of the book to delete

    Methods:
        POST: Process book deletion

    Returns:
        Redirect to book management page after successful deletion

    Access Control:
        - Requires library_staff privileges

    Logging:
        - INFO: Book deletion success
        - ERROR: Deletion failures
    """
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    book = LibraryResource.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    system_logger.log_info(f"Library staff {current_user.username} deleted book: {book_title}")
    return redirect(url_for('main.manage_books'))

@main_routes.route('/view_grades/<int:student_id>', methods=['GET'])
@login_required
def view_grades(student_id):
    """
    View grades for a specific student.

    Args:
        student_id (int): ID of the student whose grades are to be viewed

    Methods:
        GET: Display grades for the student

    Returns:
        Rendered template with student's grades

    Access Control:
        - Requires student privileges
        - Student can only view their own grades
    """
    if current_user.user_type != 'student' or current_user.id != student_id:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.index'))


    grades = StudentGrade.query.filter_by(student_id=student_id).all()

    grade_data = [
        {
            'course_name': Course.query.get(grade.course_id).course_name,
            'grade': grade.grade
        }
        for grade in grades
    ]

    return render_template('view_grades.html', grade_data=grade_data)


@main_routes.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    """Add or update student grades.

    Methods:
        GET: Display grade entry form
        POST: Process grade submission

    Returns:
        GET: Render add_grade.html with form
        POST: Redirect to course page after successful submission

    Permission:
        - Requires teacher privileges
        - Teacher must be course instructor

    Logging:
        - INFO: Grade addition/update success
        - ERROR: Grade submission failures
    """
    course_id = request.args.get('course_id', type=int)
    student_id = request.args.get('student_id', type=int)


    if current_user.user_type != 'teacher':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))


    form = AddGradeForm()
    if form.validate_on_submit():

        grade_entry = StudentGrade.query.filter_by(student_id=student_id, course_id=course_id).first()

        if grade_entry:

            grade_entry.grade = form.grade.data
            system_logger.log_info(f"Teacher {current_user.username} updated grade for student {student_id} in course {course_id}")
            flash("Grade updated successfully!", "success")
        else:

            grade_entry = StudentGrade(student_id=student_id, course_id=course_id, grade=form.grade.data)
            db.session.add(grade_entry)
            system_logger.log_info(f"Teacher {current_user.username} added new grade for student {student_id} in course {course_id}")
            flash("Grade added successfully!", "success")

        db.session.commit()
        return redirect(url_for('main.select_grade_entry'))

    return render_template('add_grade.html', form=form)


@main_routes.route('/select_grade_entry', methods=['GET', 'POST'])
@login_required
def select_grade_entry():
    """
    Select a course and student for grade entry.

    Methods:
        GET: Display selection form
        POST: Process selection and redirect to grade entry

    Returns:
        Rendered template with selection form

    Access Control:
        - Requires teacher privileges
    """
    # 检查用户权限，仅允许教师访问
    if current_user.user_type != 'teacher':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))

    # 获取当前教师创建的课程
    courses = Course.query.filter_by(created_by=current_user.id).all()

    # 初始化学生为空，在前端根据选的课程动态加载
    students = []

    return render_template('select_grade_entry.html', courses=courses, students=students)

@main_routes.route('/get_students_by_course/<int:course_id>', methods=['GET'])
@login_required
def get_students_by_course(course_id):
    """
    API endpoint to get list of students enrolled in a specific course.

    Args:
        course_id (int): ID of the course to query

    Methods:
        GET: Retrieve student list for course

    """
    # 验证该课程是否由当前教师创建
    course = Course.query.filter_by(id=course_id, created_by=current_user.id).first()
    if not course:
        return jsonify({'error': 'Unauthorized access'}), 403

    # 查询注册了该课程的学生
    registrations = CourseRegistration.query.filter_by(course_id=course_id).all()
    students = [
        {'id': reg.user_id, 'username': User.query.get(reg.user_id).username}
        for reg in registrations
    ]

    return jsonify({'students': students})

@main_routes.route('/e_bike_management', methods=['GET', 'POST'])
@login_required
def e_bike_management():
    """Manage e-bike registration and information.

    Methods:
        GET: Display e-bike management interface
        POST: Process e-bike registration/updates

    Returns:
        GET: Render e_bike_management.html with current registration
        POST: Redirect to same page after successful update

    Permission:
        - Requires user to be logged in
        - Students can only manage their own e-bike
        - Security staff can view all registrations

    Features:
        - Register new e-bike
        - Update existing registration
        - View registration status
    """
    if current_user.user_type != 'student':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))

    # 查询当前学生的电动车信息
    e_bike = EBikeLicense.query.filter_by(owner_id=current_user.id).first()
    form = EBikeForm(obj=e_bike)

    if form.validate_on_submit():
        if not e_bike:
            e_bike = EBikeLicense(owner_id=current_user.id)
        e_bike.license_plate = form.license_plate.data
        e_bike.bike_model = form.bike_model.data
        e_bike.status = 'Pending'  # 每次创建或修改后自动变为"申请"状态
        e_bike.registration_date = None
        e_bike.expiration_date = None
        e_bike.approved_by = None
        db.session.add(e_bike)
        db.session.commit()
        flash("E-bike registration updated successfully!", "success")
        return redirect(url_for('main.e_bike_management'))

    return render_template('e_bike_management.html', form=form, e_bike=e_bike)



@main_routes.route('/manage_ebikes', methods=['GET'])
@login_required
def manage_ebikes():
    """
    Display e-bike license management interface for security personnel.

    Methods:
        GET: Display all e-bike license applications

    Returns:
        Rendered manage_ebikes.html template with sorted license applications

    Access Control:
        - Requires authentication
        - Limited to security personnel only

    Database Operations:
        - Retrieves all e-bike licenses
        - Orders by license ID in descending order
    """
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    # 获取所有电动车申请，并按 ID 倒序排列
    ebikes = EBikeLicense.query.order_by(EBikeLicense.license_id.desc()).all()
    return render_template('manage_ebikes.html', ebikes=ebikes)


@main_routes.route('/approve_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def approve_ebike(ebike_id):
    """
    Approve an e-bike license application.

    Args:
        ebike_id (int): ID of the e-bike license to approve

    Methods:
        POST: Process license approval

    Returns:
        Redirect to e-bike management page after approval

    Access Control:
        - Requires authentication
        - Limited to security personnel only

    Database Updates:
        - Sets status to 'Approved'
        - Updates registration and expiration dates
        - Records approving security officer
    """
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Approved'
    ebike.registration_date = request.form['registration_date']
    ebike.expiration_date = request.form['expiration_date']
    ebike.approved_by = current_user.id
    db.session.commit()
    flash('E-bike approved successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/reject_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def reject_ebike(ebike_id):
    """
    Reject an e-bike license application.

    Args:
        ebike_id (int): ID of the e-bike license to reject

    Methods:
        POST: Process license rejection

    Returns:
        Redirect to e-bike management page after rejection

    Access Control:
        - Requires authentication
        - Limited to security personnel only

    Database Updates:
        - Sets status to 'Rejected'
    """
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Rejected'
    db.session.commit()
    flash('E-bike rejected successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/cancel_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def cancel_ebike(ebike_id):
    """
    Cancel an existing e-bike license.

    Args:
        ebike_id (int): ID of the e-bike license to cancel

    Methods:
        POST: Process license cancellation

    Returns:
        Redirect to e-bike management page after cancellation

    Access Control:
        - Requires authentication
        - Limited to security personnel only

    Database Updates:
        - Sets status to 'Cancelled'
        - Clears registration and expiration dates
        - Removes approver reference
    """
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Cancelled'
    ebike.registration_date = None
    ebike.expiration_date = None
    ebike.approved_by = None
    db.session.commit()
    flash('E-bike registration cancelled successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/visitor')
def visitor():
    """
    Display visitor information page.

    Methods:
        GET: Display visitor information

    Returns:
        Rendered visitor.html template

    Access Control:
        - Public access
        - No authentication required
    """
    return render_template('visitor.html')

@main_routes.route('/contact')
def contact():
    """
    Display contact information page.

    Methods:
        GET: Display contact information

    Returns:
        Rendered contact.html template

    Access Control:
        - Public access
        - No authentication required
    """
    return render_template('contact.html')

@main_routes.route('/admin/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    """Display user management interface for administrators.

    Returns:
        GET: Render manage_users.html with list of all users

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Data:
        - Retrieves all users from database
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    system_logger.log_info(f"Admin {current_user.username} accessed user management")
    return render_template('manage_users.html', users=users)


@main_routes.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Handle creation of new users by administrators.

    Methods:
        GET: Display user creation form
        POST: Process new user creation

    Returns:
        GET: Render create_user.html with form
        POST: 
            - Success: Redirect to manage_users
            - Failure: Redisplay form with errors

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Logging:
        - INFO: User creation success
        - ERROR: Creation failures
    """
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('该邮箱已被注册。请使用其他邮箱。', 'danger')
            return redirect(url_for('main.create_user'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            user_type=form.user_type.data
        )
        db.session.add(new_user)
        db.session.commit()
        system_logger.log_info(f"Admin {current_user.username} created new user: {new_user.username} ({new_user.user_type})")
        flash(f'用户 {form.username.data} 创建成功！', 'success')
        return redirect(url_for('main.manage_users'))
    return render_template('create_user.html', form=form)

@main_routes.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user from the system.

    Args:
        user_id (int): The ID of the user to delete

    Returns:
        POST: Redirect to manage_users page

    Permission:
        - Requires admin privileges
        - Cannot delete last admin account
        - Redirects to index if unauthorized

    Logging:
        - INFO: User deletion success
        - ERROR: Deletion failures

    Validation:
        - Checks if attempting to delete last admin
        - Handles cascade deletion of related data
    """
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))

    try:
        user = User.query.get_or_404(user_id)
        username = user.username
        user_type = user.user_type
        # 1. 根据用户类型处理特定关联数据
        if user.user_type == 'student':
            # 处理学生相关数据
            CourseRegistration.query.filter_by(user_id=user.id).delete()
            StudentGrade.query.filter_by(student_id=user.id).delete()
            EBikeLicense.query.filter_by(owner_id=user.id).delete()
            StudentProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'teacher':
            # 处理教师相关数据
            courses = Course.query.filter_by(created_by=user.id).all()
            for course in courses:
                StudentGrade.query.filter_by(course_id=course.id).delete()
                CourseRegistration.query.filter_by(course_id=course.id).delete()
            Course.query.filter_by(created_by=user.id).delete()
            TeacherProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'security':
            # 处理安保人员相关数据
            EBikeLicense.query.filter_by(approved_by=user.id).update({EBikeLicense.approved_by: None})
            SecurityProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'library_staff':
            # 处理图书管理员相关数据
            LibraryStaffProfile.query.filter_by(user_id=user.id).delete()
        
        elif user.user_type == 'admin':
            # 检查是否是最后一个管理员
            admin_count = User.query.filter_by(user_type='admin').count()
            if admin_count <= 1:
                from flask import session
                session['_flashes'] = [(u'danger', u'Cannot delete the last admin account.')]
                return redirect(url_for('main.manage_users'))
            AdminProfile.query.filter_by(user_id=user.id).delete()

        # 2. 处理论坛相关数据（除了安保人员）
        if user.user_type != 'security':
            posts = ForumPost.query.filter_by(author_id=user.id).all()
            for post in posts:
                ForumReply.query.filter_by(post_id=post.post_id).delete()
            ForumReply.query.filter_by(replier_id=user.id).delete()
            ForumPost.query.filter_by(author_id=user.id).delete()
        
        # 3. 删除用户偏好设置（所有类型用户都有）
        UserPreference.query.filter_by(user_id=user.id).delete()
        
        # 4. 最后删除用户本身
        db.session.delete(user)
        db.session.commit()
        
        system_logger.log_info(f"Admin {current_user.username} deleted user: {username} ({user_type})")
        flash('User Delete Success!', 'success')
        return redirect(url_for('main.manage_users'))
        
    except Exception as e:
        system_logger.log_error(f"Error deleting user {user_id}: {str(e)}")
        db.session.rollback()
        flash(f'Delete Error:{str(e)}', 'danger')
        return redirect(url_for('main.manage_users'))
    

@main_routes.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Handle user preference settings.

    Methods:
        GET: Display preferences form
        POST: Process preference updates

    Returns:
        GET: Render preferences.html with form
        POST: Redirect to preferences page after update

    Data:
        - Creates default preferences if none exist
        - Updates theme and font size settings

    Permission:
        - Requires user to be logged in
    """

    # 获取或创建用户偏好
    user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not user_pref:
        user_pref = UserPreference(user_id=current_user.id)
        db.session.add(user_pref)
        db.session.commit()
    
    form = UserPreferenceForm(obj=user_pref)
    
    if form.validate_on_submit():
        user_pref.theme = form.theme.data
        user_pref.font_size = form.font_size.data
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('main.preferences'))
        
    return render_template('preferences.html', form=form)

@main_routes.route('/admin/manage_courses')
@login_required
def manage_courses():
    """Display course management interface for administrators.

    Returns:
        GET: Render manage_courses.html with all courses

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Data:
        - Retrieves all courses from database
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
# Get all courses
    courses = Course.query.all()
    

    
    return render_template('manage_courses.html', courses=courses)

@main_routes.route('/admin/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course_admin(course_id):
    """Delete a course and all related data.

    Args:
        course_id (int): The ID of the course to delete

    Returns:
        POST: Redirect to manage_courses page

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Actions:
        - Deletes course grades
        - Deletes course registrations
        - Deletes forum posts and replies
        - Deletes course itself

    Logging:
        - INFO: Course deletion success
        - ERROR: Deletion failures
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))

    try:
        course = Course.query.get_or_404(course_id)
        
        # Delete all course-related data
        # 1. Delete grades
        StudentGrade.query.filter_by(course_id=course.id).delete()
        
        # 2. Delete course registrations
        CourseRegistration.query.filter_by(course_id=course.id).delete()
        
        # 3. Delete forum posts and replies
        course_posts = ForumPost.query.filter_by(course_id=course.id).all()
        for post in course_posts:
            ForumReply.query.filter_by(post_id=post.post_id).delete()
        ForumPost.query.filter_by(course_id=course.id).delete()
        
        # 4. Delete the course itself
        db.session.delete(course)
        db.session.commit()
        
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('main.manage_courses'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
        return redirect(url_for('main.manage_courses'))

@main_routes.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user information by administrator.

    Args:
        user_id (int): The ID of the user to edit

    Methods:
        GET: Display user edit form
        POST: Process user information updates

    Returns:
        GET: Render edit_user.html with form
        POST: Redirect to manage_users after successful update

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Logging:
        - INFO: User update success
        - ERROR: Update failures
    """
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():

        user.user_type = form.user_type.data
        
        if form.password.data:  # 只有当输入了新密码时才更新密码
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            
        db.session.commit()
        flash(f'User {user.username} update success !', 'success')
        return redirect(url_for('main.manage_users'))
        
    return render_template('edit_user.html', form=form, user=user)

@main_routes.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    """Ban a user from the system.

    Args:
        user_id (int): The ID of the user to ban

    Returns:
        POST: Redirect to manage_users page

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Logging:
        - WARNING: User ban events
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    system_logger.log_warning(f"Admin {current_user.username} banned user: {user.username}")
    flash(f'User {user.username} has been banned.', 'success')
    return redirect(url_for('main.manage_users'))

@main_routes.route('/admin/unban_user/<int:user_id>', methods=['POST'])
@login_required
def unban_user(user_id):
    """Remove ban from a user.

    Args:
        user_id (int): The ID of the user to unban

    Returns:
        POST: Redirect to manage_users page

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Logging:
        - INFO: User unban events
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    system_logger.log_info(f"Admin {current_user.username} unbanned user: {user.username}")
    flash(f'User {user.username} has been unbanned.', 'success')
    return redirect(url_for('main.manage_users'))

@main_routes.route('/admin/view_logs')
@login_required
def view_logs():
    """Display system logs for administrators.

    Returns:
        GET: Render view_logs.html with log content

    Permission:
        - Requires admin privileges
        - Redirects to index if unauthorized

    Features:
        - Lists all log files
        - Filters logs by type (error, warning, info)
        - Displays selected log file content
    """
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取日志文件列表
    log_dir = 'logs'
    log_files = []
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        log_files.sort(reverse=True)  # 最新的文件在前
    
    # 读取选的日志文件
    selected_log = request.args.get('file', '')
    log_content = {'errors': [], 'warnings': [], 'info': []}
    
    if selected_log and selected_log in log_files:
        with open(os.path.join(log_dir, selected_log), 'r', encoding='utf-8') as f:
            for line in f:
                if 'ERROR' in line:
                    log_content['errors'].append(line)
                elif 'WARNING' in line:
                    log_content['warnings'].append(line)
                elif 'INFO' in line:
                    log_content['info'].append(line)
    
    return render_template('view_logs.html',
                         log_files=log_files,
                         selected_log=selected_log,
                         log_content=log_content)

@main_routes.route('/account/settings', methods=['GET'])
@login_required
def account_settings():
    """Display account settings page.
    
    Returns:
        Rendered account settings template
        
    Permission:
        - Requires user to be logged in
        - Admins cannot access this page
    """
    if current_user.user_type == 'admin':
        flash('Administrators cannot delete their accounts.', 'danger')
        return redirect(url_for('main.index'))
        
    form = DeleteAccountForm()
    return render_template('account_settings.html', form=form)

@main_routes.route('/account/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Handle account deletion request."""
    if current_user.user_type == 'admin':
        flash('Administrators cannot delete their accounts.', 'danger')
        return redirect(url_for('main.index'))
        
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.password.data):
            try:
                # 开启数据库会话
                db.session.begin_nested()
                
                # 保存用户信息用于日志
                user_id = current_user.id
                username = current_user.username
                user_type = current_user.user_type
                
                system_logger.log_info(f"Starting account deletion for user: {username} ({user_type})")

                try:
                    # 1. 删除论坛相关数据
                    system_logger.log_info("Deleting forum data...")
                    reply_count = ForumReply.query.filter_by(replier_id=user_id).delete()  # 修改 user_id 为 replier_id
                    post_count = ForumPost.query.filter_by(author_id=user_id).delete()  # 修改 user_id 为 author_id
                    system_logger.log_info(f"Deleted {reply_count} replies and {post_count} posts")

                    # 2. 根据用户类型删除特定数据
                    if user_type == 'student':
                        system_logger.log_info("Deleting student data...")
                        StudentGrade.query.filter_by(student_id=user_id).delete()
                        CourseRegistration.query.filter_by(user_id=user_id).delete()
                        EBikeLicense.query.filter_by(owner_id=user_id).delete()  # 修改 student_id 为 owner_id
                        StudentProfile.query.filter_by(user_id=user_id).delete()

                    elif user_type == 'teacher':
                        system_logger.log_info("Deleting teacher data...")
                        courses = Course.query.filter_by(created_by=user_id).all()
                        for course in courses:
                            course_id = course.id
                            StudentGrade.query.filter_by(course_id=course_id).delete()
                            CourseRegistration.query.filter_by(course_id=course_id).delete()
                            ForumPost.query.filter_by(course_id=course_id).delete()
                        Course.query.filter_by(created_by=user_id).delete()
                        TeacherProfile.query.filter_by(user_id=user_id).delete()

                    elif user_type == 'security':
                        system_logger.log_info("Deleting security staff data...")
                        EBikeLicense.query.filter_by(approved_by=user_id).update({EBikeLicense.approved_by: None})
                        SecurityProfile.query.filter_by(user_id=user_id).delete()

                    elif user_type == 'library_staff':
                        system_logger.log_info("Deleting library staff data...")
                        LibraryStaffProfile.query.filter_by(user_id=user_id).delete()

                    # 3. 删除用户偏好设置
                    system_logger.log_info("Deleting user preferences...")
                    UserPreference.query.filter_by(user_id=user_id).delete()

                    # 4. 登出用户
                    system_logger.log_info("Logging out user...")
                    logout_user()

                    # 5. 删除用户账户
                    system_logger.log_info("Deleting user account...")
                    user = User.query.get(user_id)
                    if user:
                        db.session.delete(user)
                    
                    # 6. 提交所有更改
                    system_logger.log_info("Committing changes...")
                    db.session.commit()

                    system_logger.log_info(f"User account deleted successfully: {username} ({user_type})")
                    flash('Your account has been successfully deleted.', 'success')
                    return redirect(url_for('main.index'))

                except SQLAlchemyError as e:
                    system_logger.log_error(f"SQLAlchemy error during deletion: {str(e)}")
                    db.session.rollback()
                    raise

            except Exception as e:
                db.session.rollback()
                system_logger.log_error(f"Unexpected error during account deletion: {str(e)}")
                flash(f'Error deleting account: {str(e)}', 'danger')  # 显示具体错误信息
                return redirect(url_for('main.account_settings'))
        else:
            flash('Incorrect password.', 'danger')
            return redirect(url_for('main.account_settings'))
    
    # 如果表单验证失败，显示具体错误
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    return redirect(url_for('main.account_settings'))

@main_routes.errorhandler(Exception)
def handle_error(error):
    """Global error handler for all unhandled exceptions.

    Args:
        error: The exception that was raised

    Returns:
        Tuple of error message and HTTP 500 status code

    Logging:
        - ERROR: Logs all unhandled exceptions
    """
    system_logger.log_error(f"System error: {str(error)}")
    return 'Internal Server Error', 500

@main_routes.route('/ai_assistant')
@login_required
def ai_assistant():
    """
    Display AI assistant interface with chat history.

    Methods:
        GET: Display AI assistant page

    Returns:
        Rendered ai_assistant.html template with recent chat history

    Access Control:
        - Requires authentication
        - Available to all user types

    Database Operations:
        - Retrieves 10 most recent chat history entries for current user
        - Orders chat history by creation time (descending)
    """
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id)\
                                 .order_by(ChatHistory.created_at.desc())\
                                 .limit(10).all()
    return render_template('ai_assistant.html', chat_history=chat_history)

@main_routes.route('/ai_assistant/chat', methods=['POST'])
@login_required
def chat():
    """
    Handle AI chat interactions using Wenxin Yiyan API.

    Methods:
        POST: Process chat message and get AI response

    Request Body:
        JSON: {
            'message': 'User's input message'
        }

    Returns:
        Success Response: {
            'status': 'success',
            'response': 'AI generated response'
        }
        Error Response: {
            'status': 'error',
            'message': 'Error description'
        }, 500 status code

    Access Control:
        - Requires authentication
        - Customizes response based on user type

    Features:
        - Role-specific prompts based on user type:
            * Student: Learning assistance with course context
            * Teacher: Teaching methodology and course design help
            * Library Staff: Library management assistance
            * Security: Campus security guidance
        - Maintains chat history in database
        - Always responds in English

    External Services:
        - Wenxin Yiyan API for AI responses
        - Uses environment variables for API configuration

    Error Handling:
        - API connection errors
        - Invalid API responses
        - Database operation errors
    """
    message = request.json.get('message', '')
    
    # Wenxin Yiyan API configuration - 使用环境变量
    API_KEY = os.getenv('WENXIN_API_KEY')
    SECRET_KEY = os.getenv('WENXIN_SECRET_KEY')
    
    # Get access token
    def get_access_token():
        url = os.getenv('WENXIN_TOKEN_URL')
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY
        }
        return str(requests.post(url, params=params).json().get("access_token"))

    try:
        # Build different prompt words based on user type
        user_type = current_user.user_type
        if user_type == 'student':
            # Get information about the courses that students are enrolled in
            courses = Course.query.join(CourseRegistration)\
                .filter(CourseRegistration.user_id == current_user.id)\
                .all()
            
            courses_info = "\n".join([
                f"- {course.course_name}: {course.description}"
                for course in courses
            ])
            
            prompt = f"""You are a professional learning assistant helping a student.

            Student's current courses:
            {courses_info}

            As a student assistant, you should:
            1. Provide clear and easy-to-understand answers
            2. Give specific study tips and examples
            3. Encourage independent thinking
            4. Suggest appropriate learning methods for course-related questions
            5. Reference the student's current courses when relevant

            Please respond in English to this question: {message}"""
            
        elif user_type == 'teacher':
            # Get information about a course created by an instructor
            courses = Course.query.filter_by(created_by=current_user.id).all()
            
            courses_info = "\n".join([
                f"- {course.course_name}: {course.description}"
                for course in courses
            ])
            
            prompt = f"""You are a teaching assistant helping a professor.

            Professor's current courses:
            {courses_info}

            As a teaching assistant, you should:
            1. Provide teaching methodology suggestions
            2. Share course design ideas specific to the courses being taught
            3. Suggest classroom interaction methods
            4. Recommend teaching resources
            5. Consider the context of current courses when providing advice

            Please respond in English to this question: {message}"""
            
        elif user_type == 'library_staff':
            prompt = f"""You are a library management assistant helping library staff.

            As a library assistant, you should:
            1. Provide library management suggestions
            2. Help with book classification questions
            3. Suggest reader service methods
            4. Provide resource management advice

            Please respond in English to this question: {message}"""
            
        elif user_type == 'security':
            prompt = f"""You are a campus security assistant helping security personnel.

            As a security assistant, you should:
            1. Provide security management suggestions
            2. Help with security-related questions
            3. Suggest emergency response methods
            4. Provide patrol guidance

            Please respond in English to this question: {message}"""
            
        else:
            prompt = f"""You are a general assistant. Please provide a professional and helpful response in English to this question: {message}"""
        
        # Uniform request to add an English reply at the end of the prompt
        prompt += "\n\nIMPORTANT: Always respond in English, regardless of the language of the question."
        
        # Configure Wenxin Yiyan requests - 使用环境变量
        url = f"{os.getenv('WENXIN_API_URL')}?access_token={get_access_token()}"
        
        payload = json.dumps({
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Send a request to Wenxin Yiyan API
        response = requests.post(url, headers=headers, data=payload)
        result = response.json()
        
        if 'result' in result:
            answer = result['result']
            
            # Save your chat history
            chat = ChatHistory(
                user_id=current_user.id,
                message=message,
                response=answer
            )
            db.session.add(chat)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'response': answer
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get AI response'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500