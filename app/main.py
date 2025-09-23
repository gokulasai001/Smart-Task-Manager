from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import User, Project, Task
from .forms import ProjectForm, TaskForm
from . import db, mail
from flask_mail import Message
from datetime import datetime
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Admin':
        users = User.query.all()
        projects = Project.query.all()
        tasks = Task.query.all()
        stats = {
            'total_users': len(users),
            'total_projects': len(projects),
            'total_tasks': len(tasks),
            'pending_tasks': len([t for t in tasks if t.status == 'Pending'])
        }
        return render_template('dashboard_admin.html', 
                             users=users, projects=projects, tasks=tasks, stats=stats)
    
    elif current_user.role == 'Manager':
        projects = Project.query.filter_by(manager_id=current_user.id).all()
        tasks = Task.query.join(Project).filter(Project.manager_id == current_user.id).all()
        stats = {
            'my_projects': len(projects),
            'managed_tasks': len(tasks),
            'pending_tasks': len([t for t in tasks if t.status == 'Pending'])
        }
        return render_template('dashboard_manager.html', 
                             projects=projects, tasks=tasks, stats=stats)
    
    else:  # Employee
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()
        stats = {
            'my_tasks': len(tasks),
            'pending': len([t for t in tasks if t.status == 'Pending']),
            'in_progress': len([t for t in tasks if t.status == 'In Progress']),
            'completed': len([t for t in tasks if t.status == 'Completed'])
        }
        return render_template('dashboard_employee.html', tasks=tasks, stats=stats)

# Project routes
@main.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if current_user.role not in ['Admin', 'Manager']:
        flash('Access denied. Only Admins and Managers can create projects.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            manager_id=current_user.id if current_user.role == 'Manager' else None
        )
        db.session.add(project)
        db.session.commit()
        flash(f'Project "{project.name}" created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('project_form.html', title='Create Project', form=form)

# Task routes
@main.route('/tasks/create')
@main.route('/tasks/create/<int:project_id>')
@login_required
def create_task(project_id=None):
    form = TaskForm()
    
    # Set choices for assigned_to
    users = User.query.all()
    form.assigned_to.choices = [(0, 'Select User')] + [(u.id, f'{u.username} ({u.role})') for u in users]
    
    # Set choices for project_id
    if current_user.role == 'Admin':
        projects = Project.query.all()
    elif current_user.role == 'Manager':
        projects = Project.query.filter_by(manager_id=current_user.id).all()
    else:
        projects = []
    
    form.project_id.choices = [(0, 'Select Project')] + [(p.id, p.name) for p in projects]
    
    # Pre-select project if provided
    if project_id:
        form.project_id.data = project_id
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            assigned_to=form.assigned_to.data if form.assigned_to.data != 0 else None,
            project_id=form.project_id.data if form.project_id.data != 0 else None
        )
        db.session.add(task)
        db.session.commit()
        
        # Send email notification
        if task.assigned_to:
            assignee = User.query.get(task.assigned_to)
            try:
                msg = Message(
                    subject='New Task Assigned',
                    recipients=[assignee.email],
                    body=f'Hi {assignee.username},\n\nYou have been assigned a new task:\n\nTitle: {task.title}\nPriority: {task.priority}\nDue Date: {task.due_date or "No due date"}\n\nDescription:\n{task.description or "No description provided"}\n\nBest regards,\nSmart Task Manager'
                )
                mail.send(msg)
                flash(f'Task created and notification sent to {assignee.username}!', 'success')
            except Exception as e:
                flash(f'Task created but email notification failed: {str(e)}', 'warning')
        else:
            flash('Task created successfully!', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('task_form.html', title='Create Task', form=form)

# API routes for analytics
@main.route('/api/task-stats')
@login_required
def task_stats():
    if current_user.role == 'Admin':
        tasks = Task.query.all()
    elif current_user.role == 'Manager':
        tasks = Task.query.join(Project).filter(Project.manager_id == current_user.id).all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    
    stats = {
        'pending': len([t for t in tasks if t.status == 'Pending']),
        'in_progress': len([t for t in tasks if t.status == 'In Progress']),
        'completed': len([t for t in tasks if t.status == 'Completed'])
    }
    
    return jsonify(stats)

@main.route('/api/priority-stats')
@login_required
def priority_stats():
    if current_user.role == 'Admin':
        tasks = Task.query.all()
    elif current_user.role == 'Manager':
        tasks = Task.query.join(Project).filter(Project.manager_id == current_user.id).all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    
    stats = {
        'low': len([t for t in tasks if t.priority == 'Low']),
        'medium': len([t for t in tasks if t.priority == 'Medium']),
        'high': len([t for t in tasks if t.priority == 'High'])
    }
    
    return jsonify(stats)