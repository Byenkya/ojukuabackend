from application.models.model import (LoanOfficer, loan_officer_schema, loan_officers_schema,LoanType,loan_type_schema,
loan_types_schema,User,Loan)
from flask import request, Blueprint, make_response
import json
import os

officer = Blueprint('officer', __name__, url_prefix="/officer")

@officer.route("/", methods=["POST"])
def add_loan_officer():
    first_name = request.json["first_name"]
    surname = request.json["surname"]
    sex = request.json["sex"]
    email = request.json["email"]
    telephone = request.json["telephone"]
    role = request.json["user_role"]
    password = request.json["password"]

    officer = LoanOfficer(first_name,surname,sex,email,telephone,role)

    user = User(telephone,password,role,officer)

    if officer and user:
        return {'state': False}
    else:
        return {'state': True}

@officer.route("/", methods=["GET"])
def get_officers():
    loan_officers = LoanOfficer.get_officers(LoanOfficer)
    return loan_officers_schema.dumps(loan_officers)

@officer.route("/delete_officer/<id>", methods=["GET"])
def delete_officer(id):
    LoanOfficer.delete_officer(LoanOfficer,id)

    return {"operation":"Success"}


@officer.route("/add_product", methods=["POST"])
def add_product():
    loan_name = request.json['loan_name']
    rate = request.json['interest_rate']
    description = request.json['description']

    LoanType(loan_name,rate,description)

    return request.json

@officer.route("/get_loan_types", methods=["GET"])
def get_loan_types():
    loan_types = LoanType.get_loan_types(LoanType)

    return loan_types_schema.dumps(loan_types)


@officer.route("/update_loan_type/<id>", methods=["POST"])
def update_loan_type(id):
    loan_name = request.json["loan_name"]
    interest_rate = request.json["interest_rate"]
    description = request.json["description"]

    LoanType.update_loan_type(LoanType,id,loan_name,interest_rate,description)

    return request.json

@officer.route("/delete_loan_type/<id>", methods=["GET"])
def delete_loan_type(id):
    LoanType.delete_loan_type(LoanType,id)

    return {"operation": "success"}

@officer.route("/get_officer_details/<username>", methods=["GET"])
def get_details(username):
    return LoanOfficer.get_officer(LoanOfficer,username)

@officer.route("/change_password/<username>", methods=["POST"])
def change_password(username):
    new_password = request.json['childling']
    old_password = request.json['old']
    User.change_password(User,username,old_password,new_password)

    return request.json

@officer.route("/forward_manager/<id>", methods=["POST"])
def forward_mag(id):
    reason = request.json['reason']
    Loan.forward_manager(Loan,id,reason)

    return request.json

@officer.route("/forward_ceo/<id>", methods=["POST"])
def forward_CEO(id):
    reason = request.json['reason']
    Loan.forward_ceo(Loan,id,reason)

    return request.json

@officer.route("/bussiness-sum", methods=["GET"])
def buz_sum():
    summary = LoanOfficer.bus_sum(LoanOfficer)

    return summary
