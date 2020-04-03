from application.models.model import Loan, loan_schema, loans_schema, Client, Collateral, Payment, payment_schema, payments_schema
from flask import request, Blueprint, make_response, jsonify, url_for, send_file
import json
import os
from datetime import datetime

loan = Blueprint('loan', __name__, url_prefix="/loan")

@loan.route("/", methods=["GET"])
def get_clients():
    loans = Loan.get_loans(Loan)
    return loans_schema.dumps(loans)

@loan.route("/client_loan_req_info/<id>", methods=["GET"])
def getRequest(id):
    return Loan.get_loan_request(Loan,id)


@loan.route("/view_file/<filename>/<id>", methods=["GET"])
def get_file(filename,id):
    loan = Loan.get_client_loan(Loan, id)
    for file in loan.collaterals[0].files:
        if file.filename == filename:
            file_path = os.path.join("./application/static",file.filename)
            abs_path = os.path.abspath(os.path.dirname(__file__))
            path = abs_path.replace("/views/Loan","/static")
            return send_file(path+"/"+file.filename, mimetype='application/pdf')


@loan.route("/view_image/<id>", methods=["GET"])
def get_image(id):
    loan = Loan.get_client_loan(Loan, id)
    file_path = os.path.join("./application/static", loan.collaterals[0].image)
    abs_path = os.path.abspath(os.path.dirname(__file__))
    path = abs_path.replace("/views/Loan","/static")

    return send_file(path+"/"+loan.collaterals[0].image, mimetype='image/*')

@loan.route("/view_letter/<id>", methods=["GET"])
def view_letter(id):
    loan = Loan.get_client_loan(Loan, id)
    file_path = os.path.join("./application/static", loan.G_LC_letter)
    abs_path = os.path.abspath(os.path.dirname(__file__))
    path = abs_path.replace("/views/Loan","/static")

    print(loan.G_LC_letter)

    return send_file(path+"/"+loan.G_LC_letter, mimetype='application/pdf')

@loan.route("/reject_loan/<id>", methods=["POST"])
def reject(id):
    rejection_reason = request.json["rejection_reason"]
    Loan.reject_loan(Loan, id, rejection_reason)

    return request.json

@loan.route("/accept_loan/<id>", methods=["GET"])
def accept(id):
    Loan.accept_loan(Loan, id)

    return json.dumps({"operation":"True"})

@loan.route("/issue_payment/<id>", methods=["GET"])
def issue_payment(id):
    Loan.issue_payment(Loan,id)

    return json.dumps({"operation":"True"})

@loan.route("/delete_loan/<id>", methods=["GET"])
def delete(id):
    Loan.delete_loan(Loan, id)

    return json.dumps({"operation":"True"})

@loan.route("/get_client_loans/<id>", methods=["GET"])
def get_client_loans(id):
    loans = Loan.get_client_loans(Loan,id)

    return loans_schema.dumps(loans)

@loan.route("/get_loan_details/<id>", methods=["POST"])
def getLoan(id):
    status = request.json["status"]

    return Loan.get_loan_details(Loan,id,status)

@loan.route("/pay_loan/<id>", methods=["POST"])
def pay_loan(id):#client_id
    paid = int(request.json["amount"])
    loan = Loan.pay_loan(Loan,id)
    to_pay = loan.principle_interest
    date = datetime.now()
    if loan.pay:
        Payment.make_payment(Payment,to_pay,paid,date,loan.id,loan)
    else:
        balance = to_pay - paid
        Payment(to_pay,paid,date,balance,loan)
        Loan.update_pay(Loan,loan.id,balance)


    Loan.check_balance(Loan,loan.id)

    return request.json

@loan.route("/payment_details/<id>", methods=["GET"])
def payment_details(id):
    payments = Loan.check_payments(Loan, id)
    return payments_schema.dumps(payments)
