from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from src.users.models import Users, User_Logs
from src.manager.forms import SortForm


manager = Blueprint('manager', __name__)


@manager.route('/dashboard/manager')
@login_required
def dashboard():
    return render_template('manager/dashboard.html')


@manager.route('/dashboard/manager/logs', methods=['GET', 'POST'])
@login_required
def logs():
    page_num = request.args.get('page', 1, int)
    
    form = SortForm()
    logs = User_Logs.query.join(
            Users, User_Logs.user_id == Users.id
            ).order_by(
                User_Logs.log_id.desc()
                ).add_columns(
                    User_Logs.log_id, User_Logs.user_id, User_Logs.log_type, User_Logs.log_date, User_Logs.log_time, Users.username, Users.role
                    ).paginate(page=page_num, per_page=12)

    if form.validate_on_submit():
        role = form.role.data
        date = form.date.data
        order = form.order.data
        count = int(form.count.data)
        
        # New first order
        if order == 'desc':
            if role == "All":    
                logs = User_Logs.query.join(
                        Users, User_Logs.user_id == Users.id
                        ).filter(
                            User_Logs.log_date == date
                            ).order_by(User_Logs.log_id.desc()
                                       ).add_columns(User_Logs.log_id, User_Logs.user_id, User_Logs.log_type, User_Logs.log_date, User_Logs.log_time, Users.username, Users.role
                                                     ).paginate(page=page_num, per_page=count)
                                
                return render_template('manager/logs.html', title='Activity Logs', logs=logs, form=form)
            else:
                logs = User_Logs.query.join(
                        Users, User_Logs.user_id == Users.id
                        ).filter(
                            Users.role == role, User_Logs.log_date == date
                            ).order_by(
                                User_Logs.log_id.desc()
                                ).add_columns(
                                    User_Logs.log_id, User_Logs.user_id, User_Logs.log_type, User_Logs.log_date, User_Logs.log_time, Users.username, Users.role
                                    ).paginate(page=page_num, per_page=count)
                    
                return render_template('manager/logs.html', title='Activity Logs', logs=logs, form=form)
            
        # Old first order
        else:
            if role == "All":
                logs = User_Logs.query.join(
                        Users, User_Logs.user_id == Users.id
                        ).filter(
                            User_Logs.log_date == date
                            ).order_by(
                                User_Logs.log_id
                                ).add_columns(
                                    User_Logs.log_id, User_Logs.user_id, User_Logs.log_type, User_Logs.log_date, User_Logs.log_time, Users.username, Users.role
                                    ).paginate(page=page_num, per_page=count)

                return render_template('manager/logs.html', title='Activity Logs', logs=logs, form=form)
            else:
                logs = User_Logs.query.join(
                        Users, User_Logs.user_id == Users.id
                        ).filter(
                            Users.role == role, User_Logs.log_date == date
                            ).order_by(
                                User_Logs.log_id
                                ).add_columns(
                                    User_Logs.log_id, User_Logs.user_id, User_Logs.log_type, User_Logs.log_date, User_Logs.log_time, Users.username, Users.role
                                    ).paginate(page=page_num, per_page=count)

                return render_template('manager/logs.html', title='Activity Logs', logs=logs, form=form)
            

    return render_template('manager/logs.html', title='Activity Logs', logs=logs, form=form)

