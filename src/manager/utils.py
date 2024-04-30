from datetime import datetime, timedelta
from src.users.models import Users, User_Logs


def users_pie_data() -> dict:
    """### Data for Pie Chart
    #### Return:
    A dictionary with the total count of each user's role from 'Users' table
    """
    managers = [
        {
            "labels": ["Male", "Female"],
            "values": [
                Users.query.filter(Users.role == "Manager")
                .filter(Users.gender == "Male")
                .count(),
                Users.query.filter(Users.role == "Manager")
                .filter(Users.gender == "Female")
                .count(),
            ],
            "type": "pie",
        }
    ]
    patients = [
        {
            "labels": ["Male", "Female"],
            "values": [
                Users.query.filter(Users.role == "Patient")
                .filter(Users.gender == "Male")
                .count(),
                Users.query.filter(Users.role == "Patient")
                .filter(Users.gender == "Female")
                .count(),
            ],
            "type": "pie",
        }
    ]
    doctors = [
        {
            "labels": ["Male", "Female"],
            "values": [
                Users.query.filter(Users.role == "Doctor")
                .filter(Users.gender == "Male")
                .count(),
                Users.query.filter(Users.role == "Doctor")
                .filter(Users.gender == "Female")
                .count(),
            ],
            "type": "pie",
        }
    ]
    doctors = [{"labels": ["Male", "Female"], "values": [9, 2], "type": "pie"}]
    # pie_data = {"man": managers, "pat": patients, "doc": doctors}
    return {"man": managers, "pat": patients, "doc": doctors}


def user_logs_bar_data(days=7) -> list:
    """### Data for bar graph
    
    #### Keyword arguments:
    days(int) -- Number of days to calculate logs amount, default=7
    #### Return:
    A list with Labels, Values, Type, Orientation and Marker color
    """
    # Calculate the date range for the past week
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Query the database to get logs count grouped by user role for the past week
    logs_by_role = {}
    roles = ["Patient", "Doctor", "Manager"]  # Define roles

    for role in roles:
        logs_by_role[role] = (
            User_Logs.query.join(Users)
            .filter(
                User_Logs.log_date >= start_date,
                User_Logs.log_date <= end_date,
                Users.role == role,
            )
            .count()
        )

    logs = [
        {
            "x": [
                logs_by_role["Manager"],
                logs_by_role["Doctor"],
                logs_by_role["Patient"],
            ],
            "y": ["Managers", "Doctors", "Patients"],
            "type": "bar",
            "orientation": "h",
            "marker": {"color": "#0a3622"},
        }
    ]
    
    return logs
