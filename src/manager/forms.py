from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import date


class SortForm(FlaskForm):
    role = SelectField('Role',
                       validators=[DataRequired()], choices=[('All', 'All'),
                                                             ('Patient', 'Patients'),
                                                             ('Doctor', 'Doctors'),
                                                             ('Manager', 'Managers')])
    order = SelectField('Order By',
                        validators=[DataRequired()], choices=[('desc', 'New First'),
                                                              ('asc', 'Old First')])
    date = DateField('Date', validators=[
        DataRequired()], default=date.today)

    count = SelectField('Per Page',
                        validators=[DataRequired()], choices=[(12, '12'),
                                                              (15, '15'),
                                                              (20, '20'),
                                                              (25, '25'),
                                                              (30, '30'),
                                                              (40, '40'),
                                                              (50, '50'),
                                                              (60, '60'),
                                                              (70, '70'),
                                                              (80, '80'),
                                                              (90, '90'),
                                                              (100, '100')])

    submit = SubmitField('Show')
