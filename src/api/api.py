from flask import Blueprint, jsonify, request
from src.users.models import Users, Patients, Managers, User_Logs
from src.patient.models import Payments


api = Blueprint("api", __name__)


@api.route("/api/public/log/<log_id>")
def log(log_id):
    log: User_Logs = User_Logs.query.filter_by(log_id=int(log_id)).first()
    if log:
        response = [{"result": "success"}]
        log_data = {
            "log_id": log.log_id,
            "log_type": log.log_type,
            "log_date": str(log.log_date),
            "log_time": str(log.log_time),
            "log_desc": log.log_desc,
        }
        response.append({"log": log_data})
    else:
        response = [{"result": "fail"}]

    return jsonify(response)


@api.route("/api/public/payment/<invoice_id>")
def payment_info_public(invoice_id):
    payment: Payments = (
        Payments.query.filter_by(payment_invoice_id=int(invoice_id))
        .add_columns(
            Payments.payment_id,
            Payments.payment_method,
            Payments.payment_amount,
            Payments.payment_date,
            Payments.payment_time,
        )
        .first()
    )
    if payment:
        response = [{"result": "success"}]
        info = {
            "payment_id": payment.payment_id,
            "payment_amount": payment.payment_amount,
            "payment_date": str(payment.payment_date),
            "payment_time": str(payment.payment_time),
            "payment_method": payment.payment_method,
        }
        response.append({"info": info})
    else:
        response = [{"result": "fail"}]

    return jsonify(response)


@api.route("/api/manager/payment/<invoice_id>")
def payment_info(invoice_id):
    payment = (
        Payments.query.filter(Payments.payment_invoice_id == int(invoice_id))
        .join(Payments, Managers.m_id == Payments.payment_manager_id)
        .add_columns(
            Managers.m_id,
            Managers.first_name,
            Managers.last_name,
            Managers.phone,
            Payments.payment_id,
            Payments.payment_amount,
            Payments.payment_date,
            Payments.payment_time,
            Payments.payment_method,
            Payments.payment_note,
        )
        .first()
    )
    if payment:
        response = [{"result": "success"}]
        info = {
            "manager_id": payment.m_id,
            "manager_fname": payment.first_name,
            "manager_lname": payment.last_name,
            "manager_phone": payment.phone,
            "payment_id": payment.payment_id,
            "payment_amount": payment.payment_amount,
            "payment_date": str(payment.payment_date),
            "payment_time": str(payment.payment_time),
            "payment_method": payment.payment_method,
            "payment_note": payment.payment_note,
        }
        response.append({"info": info})
    else:
        response = [{"result": "fail"}]

    return jsonify(response)


@api.route("/api/manager/search_patient", methods=["GET", "POST"])
def search_patient():
    if request.method == "POST":
        search_by = request.form.get("search_by")
        keyword = request.form.get("keyword")

        # Search By Username
        if search_by == "username":
            patients = (
                Users.query.filter(Users.username.like(f"%{keyword}%"))
                .join(Patients, Users.id == Patients.p_id)
                .add_columns(
                    Users.id,
                    Users.username,
                    Users.gender,
                    Users.email,
                    Patients.first_name,
                    Patients.last_name,
                    Patients.birthdate,
                    Patients.avatar,
                )
                .all()
            )
            # If results available
            if patients:
                response = [{"result": "success"}]
                p_data = []
                for pat in patients:
                    res = {
                        "id": pat[1],
                        "username": pat[2],
                        "gender": pat[3],
                        "email": pat[4],
                        "first_name": pat[5],
                        "last_name": pat[6],
                        "birthdate": str(pat[7]),
                        "avatar": pat[8],
                    }
                    p_data.append(res)
                response.append({"patients": p_data})

                return jsonify(response)

        # Search by User ID
        elif search_by == "id":
            patient = (
                Users.query.filter(Users.id == int(keyword))
                .join(Patients, Users.id == Patients.p_id)
                .add_columns(
                    Users.id,
                    Users.username,
                    Users.gender,
                    Users.email,
                    Patients.first_name,
                    Patients.last_name,
                    Patients.birthdate,
                    Patients.avatar,
                )
                .first()
            )

            # If results available
            if patient:
                response = [{"result": "success"}]
                res = {
                    "id": patient.id,
                    "username": patient.username,
                    "gender": patient.gender,
                    "email": patient.email,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "birthdate": str(patient.birthdate),
                    "avatar": patient.avatar,
                }
                response.append({"patients": [res]})

                return jsonify(response)

        # Search by User Email
        elif search_by == "email":
            patients = (
                Users.query.filter(Users.email.like(f"%{keyword}%"))
                .join(Patients, Users.id == Patients.p_id)
                .add_columns(
                    Users.id,
                    Users.username,
                    Users.gender,
                    Users.email,
                    Patients.first_name,
                    Patients.last_name,
                    Patients.birthdate,
                    Patients.avatar,
                )
                .all()
            )
            # If results available
            if patients:
                response = [{"result": "success"}]
                p_data = []
                for pat in patients:
                    res = {
                        "id": pat[1],
                        "username": pat[2],
                        "gender": pat[3],
                        "email": pat[4],
                        "first_name": pat[5],
                        "last_name": pat[6],
                        "birthdate": str(pat[7]),
                        "avatar": pat[8],
                    }
                    p_data.append(res)
                response.append({"patients": p_data})

                return jsonify(response)

        return jsonify([{"result": "fail"}])


@api.route("/test")
def test():
    return jsonify([{"result": "success"}])
