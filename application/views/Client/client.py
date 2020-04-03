from application.models.model import (
    Client,
    client_schema,
     clients_schema,
     Loan,
     Collateral,
     changeDate,
     User,
     Documents,
     UserClient,
     session
)
from flask import request, Blueprint, make_response, g,abort
from werkzeug.utils import secure_filename
import os
import ast
import json
from flask_httpauth import HTTPBasicAuth
from application import app

auth = HTTPBasicAuth()
basedir = os.path.abspath(os.path.dirname(__file__))
client = Blueprint('client', __name__, url_prefix="/client")

@client.route("/", methods=["POST"])
# @auth.login_required
def add_client():
    first_name = request.json["fname"]
    surname = request.json["sname"]
    dob = request.json["dob"]
    email = request.json["email"]
    telephone = request.json["telephone"]
    NIN = request.json["NIN"]
    sex = request.json["sex"]
    county = request.json["county"]
    parish = request.json["parish"]
    village = request.json["village"]
    work_place = request.json["work_place"]
    work_place_county = request.json["county"]
    work_place_parish = request.json["parish"]
    work_place_village = request.json["village"]
    NOK_first_name = request.json["NOK_fname"]
    NOK_surname = request.json["NOK_sname"]
    NOK_telephone = request.json["NOK_telephone"]
    NOK_county = request.json["NOK_county"]
    NOK_parish = request.json["NOK_parish"]
    NOK_village = request.json["NOK_village"]
    password = request.json["password"]

    address = county + " " + parish + " " + village
    work_place_address = work_place_county + " " + work_place_parish + " " + work_place_village
    NOK_address = NOK_county + " " + NOK_parish + " " + NOK_village

    client = Client(first_name, surname, dob, sex, telephone, email, NIN, address,
                    work_place, work_place_address, NOK_first_name, NOK_surname, NOK_address, NOK_telephone,
                    NOK_address)

    user = UserClient(telephone,password,client)
    if client and user:
        return {'state': False}
    else:
        return {'state': True}

# signup i.e client
@client.route("/signup", methods=["POST"])
def signup():
    first_name = request.json["fname"]
    surname = request.json["sname"]
    dob = request.json["dob"]
    email = request.json["email"]
    telephone = request.json["telephone"]
    NIN = request.json["NIN"]
    sex = request.json["sex"]
    county = request.json["county"]
    parish = request.json["parish"]
    village = request.json["village"]
    work_place = request.json["work_place"]
    work_place_county = request.json["county"]
    work_place_parish = request.json["parish"]
    work_place_village = request.json["village"]
    NOK_first_name = request.json["NOK_fname"]
    NOK_surname = request.json["NOK_sname"]
    NOK_telephone = request.json["NOK_telephone"]
    NOK_county = request.json["NOK_county"]
    NOK_parish = request.json["NOK_parish"]
    NOK_village = request.json["NOK_village"]
    password = request.json["password"]

    address = county + " " + parish + " " + village
    work_place_address = work_place_county + " " + work_place_parish + " " + work_place_village
    NOK_address = NOK_county + " " + NOK_parish + " " + NOK_village

    client = Client(first_name, surname, dob, sex, telephone, email, NIN, address,
                    work_place, work_place_address, NOK_first_name, NOK_surname, NOK_address, NOK_telephone,
                    NOK_address)
    user = UserClient(telephone,password,client)

    if client and user:
        return {'state': False}
    else:
        return {'state': True}


@client.route("/", methods=["GET"])
def get_clients():
    clients = Client.read(Client)
    return clients_schema.dumps(clients)


@client.route("/update/<id>", methods=["PUT"])
def update_client(id):
    client = Client.read_client(Client, id)
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    telephone = request.form["telephone"]
    NIN = request.form["NIN"]
    physical_address = request.form["physical_address"]
    registration_date = request.form["registration_date"]
    client.update(first_name, last_name, telephone, NIN, physical_address, registration_date)
    return client_schema.dumps(client)


@client.route("/delete/<id>", methods=["DELETE"])
def delete_client(id):
    client = Client.read_client(Client, id)
    client.delete(client)
    clients = client.read()
    return clients_schema.jumps(clients)

@client.route("/loanRequest/<id>", methods=["POST"])
def loanRequest(id):
    if request.files:
        for file_name in request.files:
            file_path = os.path.join("./application/static",file_name)
            file = request.files[file_name]
            file.save(file_path)

        client_loan_information = ast.literal_eval(request.headers["loan-information"])["_map"]
        amount_requested = client_loan_information['loan_amount_requested']
        previous_loan_performance = client_loan_information['previous_loan_records']
        amount_issued = client_loan_information['issued_amount']
        interest_rate = client_loan_information['interest_rate']
        loan_type = client_loan_information['loan_type']
        interest = client_loan_information['interest']
        principle_interest = client_loan_information['principle_interest']
        issue_date = changeDate(client_loan_information['issue_date'])
        pay_date = changeDate(client_loan_information['pay_date'])
        range = pay_date - issue_date
        period = range.days

        guarantor_names = client_loan_information['guarantors_names']
        guarantor_dob = changeDate(client_loan_information['gdob_date'])
        guarantor_sex = client_loan_information['sex']
        guarantor_nin = client_loan_information['gnin']
        guarantor_telephone = "+256" + client_loan_information['telephone_number']
        guarantor_email = client_loan_information['email']
        guarantor_residence = client_loan_information['residence']
        guarantor_occupation = client_loan_information['occupation']
        guarantor_work_place = client_loan_information['work_place']
        guarantor_work_place_address = client_loan_information['work_place_address']
        guarantor_lc1 = client_loan_information['LC1']

        client = Client.read_client(Client,id)
        client_names = " ".join([client.surname,client.first_name])
        Client.change_state(Client,id)

        # loan
        loan = Loan(
                    client_names,amount_requested,period,previous_loan_performance,amount_issued,interest_rate,loan_type,interest,
                    principle_interest,principle_interest,guarantor_names,guarantor_dob,guarantor_telephone,
                    guarantor_email,guarantor_residence,guarantor_work_place,guarantor_work_place_address,
                    guarantor_occupation,guarantor_nin,guarantor_lc1,pay_date,client
                    )

        # collaterals
        asset_name = client_loan_information['asset_name']
        value = client_loan_information['value']
        location = client_loan_information['location']
        description = client_loan_information['description']
        image = client_loan_information['collateral_image_file']

        # loan = Loan.getClientLoan(Loan, id)

        collateral = Collateral(asset_name,value,location,description,image,loan)

        for file in client_loan_information['supporting_files']['files']:
            Documents(file['name'],collateral)

        return True

    else:
        return False



@client.route("/get_clients_issued/", methods=["GET"])
def get_issued():
    clients = Client.issued_clients(Client)

    return json.dumps({'clients':clients})

@client.route("/api/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@app.route("/login/", methods=["POST"])
def login():
    username = request.json['parent']
    password = request.json['child']
    token = User.check_user(User,username,password)

    if token:
        return {'token':token}
    else:
        return {'token':False}

@app.route("/login_client/", methods=["POST"])
def login_client():
    username = request.json['parent']
    password = request.json['child']
    token = UserClient.check_user(UserClient,username,password)

    if token:
        return {'token':token}
    else:
        return {'token':False}


@app.before_request
def before_request():
    if str(request) == "<Request 'http://10.0.2.2:9090/login/' [POST]>":
        pass
    elif str(request) == "<Request 'http://10.0.2.2:9090/login_client/' [POST]>":
        pass
    elif str(request) == "<Request 'http://10.0.2.2:9090/client/signup' [POST]>":
        pass
    else:
        token = request.headers.get('Authorization')
        if token:
            token = token.replace("Bearer ","")
            user_ojukua = User.verify_auth_token(token)
            user_client = UserClient.verify_auth_token(token)
            if user_ojukua:
                pass
            elif user_client:
                pass
            else:
                return abort(401)
        else:
            return abort(401)

# ojukua client mobile application routes.
@client.route("/get_home_details/<username>", methods=['GET'])
def get_home_details(username):
    return UserClient.home_page_details(UserClient, username)

@client.route("/change_password/<username>", methods=["POST"])
def change_password(username):
    new_password = request.json['childling']
    old_password = request.json['old']
    UserClient.change_password(UserClient,username,old_password,new_password)

    return request.json
