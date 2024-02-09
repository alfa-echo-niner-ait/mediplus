from flask import Blueprint, jsonify, request
from src.users.models import Users, Patients


api = Blueprint("api", __name__)


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
