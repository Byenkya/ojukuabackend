from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, DateTime , Boolean
from sqlalchemy.orm import sessionmaker,scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, exc
from werkzeug.security import generate_password_hash, check_password_hash
from application import app

import datetime
import os
from marshmallow_sqlalchemy import ModelSchema
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,BadSignature,SignatureExpired)

basedir = os.path.abspath(os.path.dirname(__file__))
path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
engine = create_engine(path,connect_args={'check_same_thread': False})
session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

class UserClient(Base):
    __tablename__ = 'client_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, unique=True)
    password_hash = Column(String(64))
    client_id = Column(Integer, ForeignKey('client.id'))

    def __init__(self,username,password,client_id):
        self.username = username
        self.hash_password(password)
        self.add_client(client_id)
        #check client already exits
        client = session.query(UserClient).filter_by(username=username).first()
        try:
            session.add(self)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return None

    def add_client(self,client):
        client.user = self

    def check_user(self,username,password):
        user = session.query(self).filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return False
        else:
            return {'token':user.generate_auth_token()}

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id':self.id})

    def change_password(self,username,old_password,new_password):
        user = session.query(self).filter_by(username=username).first()
        if user.verify_password(old_password):
            user.password_hash = generate_password_hash(new_password)
            session.commit()
            session.close()

    def home_page_details(self, username):
        home_page = {}
        products = []
        user = session.query(Client).filter_by(telephone=username).first()
        if user:
            pdts = session.query(LoanType).all()
            total_clients = session.query(func.count(Client.id)).scalar()
            home_page['total_clients'] = total_clients
            home_page['client_id'] = user.id
            home_page['first_name'] = user.first_name
            home_page['surname'] = user.surname
            home_page['NIN'] = user.NIN
            home_page['sex'] = user.sex
            home_page['telephone'] = user.telephone
            home_page['email'] = user.email
            home_page['state'] = user.state
            if pdts:
                for product in pdts:
                    pdt = {}
                    pdt['product_name'] = product.loan_name
                    pdt['interest_rate'] = product.interest_rate
                    pdt['description'] = product.description
                    products.append(pdt)
                home_page['products'] = products

            return home_page
        else:
            return None


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None #invalid token
        user = session.query(UserClient).filter_by(id=data['id']).first()
        return user


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, unique=True)
    password_hash = Column(String(64))
    role = Column(String(20))
    officer_id = Column(Integer, ForeignKey('officer.id'))

    def __init__(self,username,password,role,officer):
        self.username = username
        self.role = role
        self.hash_password(password)
        self.add_officer(officer)

        #check if user already exits
        user = session.query(User).filter_by(username=username).first()
        try:
            session.add(self)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return None

    def add_officer(self,officer):
        officer.user = self

    def check_user(self,username,password):
        user = session.query(self).filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return False
        else:
            return {'token':user.generate_auth_token(),'responsibility':user.role}

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id':self.id})

    def change_password(self,username,old_password,new_password):
        user = session.query(self).filter_by(username=username).first()
        if user.verify_password(old_password):
            user.password_hash = generate_password_hash(new_password)
            session.commit()
            session.close()


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None #invalid token
        user = session.query(User).filter_by(id=data['id']).first()
        return user

class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    surname = Column(String)
    dob = Column(String)
    sex = Column(String)
    NIN = Column(String)
    telephone = Column(String,unique=True)
    email = Column(String)
    residence = Column(String)
    work_place = Column(String)
    work_place_address = Column(String)
    NOK_first_name = Column(String)
    NOK_surname = Column(String)
    NOK_email = Column(String)
    NOK_telephone = Column(Integer)
    NOK_residence = Column(String)
    LC_letter = Column(String)
    scanned_NID = Column(String)
    state = Column(Boolean, default=False)
    registration_date = Column(DateTime, default=datetime.datetime.now())
    loans = relationship("Loan", backref="client")
    user = relationship("UserClient", uselist=False, backref="client_users")

    def __init__(self, first_name, surname, dob, sex, telephone, email, NIN, residence,
                 work_place, work_place_address, NOK_first_name, NOK_surname, NOK_email, NOK_telephone, NOK_residence):
        self.first_name = first_name
        self.surname = surname
        self.dob = dob
        self.sex = sex
        self.telephone = telephone
        self.email = email
        self.NIN = NIN
        self.residence = residence
        self.work_place = work_place
        self.work_place_address = work_place_address
        self.NOK_first_name = NOK_first_name
        self.NOK_surname = NOK_surname
        self.NOK_email = NOK_email
        self.NOK_telephone = NOK_telephone
        self.NOK_residence = NOK_residence
        #check if user exits in database
        client = session.query(Client).filter_by(telephone=telephone).first()
        try:
            session.add(self)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return None

    def read(self):
        return session.query(self).all()

    def read_client(self, id):
        return session.query(self).filter_by(id=id).first()

    def update(self, first_name, last_name, telephone, NIN, physical_address):
        self.first_name = first_name
        self.last_name = last_name
        self.telephone = telephone
        self.NIN = NIN
        self.physical_address = physical_address
        session.commit()

    def change_state(self,id):
        client = session.query(self).filter_by(id=id).first()
        client.state = True
        session.commit()

    def issued_clients(self):
        debtors = []
        clients = session.query(self).all()
        for client in clients:
            client_loan_information = {}
            for loan in client.loans:
                if loan.status == "issued":
                    client_loan_information['id'] = client.id
                    client_loan_information['client_names'] = " ".join([client.surname,client.first_name])
                    client_loan_information['client_dob'] = client.dob
                    client_loan_information['client_nin'] = client.NIN
                    client_loan_information['client_sex'] = client.sex
                    client_loan_information['client_telephone'] = client.telephone
                    client_loan_information['client_email'] = client.email
                    client_loan_information['client_residence'] = client.residence
                    client_loan_information['client_work_place'] = client.work_place
                    client_loan_information['client_work_place_address'] = client.work_place_address
                    client_loan_information['period'] = loan.period
                    client_loan_information['amount_issued'] = loan.amount_issued
                    client_loan_information['return'] = loan.principle_interest
                    client_loan_information['balance'] = loan.balance

                    debtors.append(client_loan_information)

        return debtors

    def delete(self, client):
        session.delete(client)
        session.commit()

class LandMortgage(Base):
    __tablename__ = "landmortgage"
    id = Column(Integer, primary_key=True)
    location = Column(String)
    measurement = Column(String)
    agreement_doc = Column(String)
    loan = Column(Integer, ForeignKey('loan.id'))

    def __init__(self,location,measurement,agreement_doc,loan):
        self.location = location
        self.measurement = measurement
        self.agreement_doc = agreement_doc
        self.loan = loan
        session.add(self)
        session.commit()

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    to_pay = Column(Integer)
    paid = Column(Integer)
    date = Column(DateTime)
    balance = Column(Integer)
    loan_id = Column(Integer, ForeignKey('loan.id'))

    def __init__(self,to_pay,paid,date,balance,loan):
        self.to_pay = to_pay
        self.paid = paid
        self.date = date
        self.balance = balance
        loan.payments.append(self)
        session.add(self)
        session.commit()

    def make_payment(self,to_pay,paid,date,loan_id,loan):
        bal = []
        payments = session.query(self).filter_by(loan_id=loan_id).all()
        for payment in payments:
            bal.append(payment.balance)
        balance = bal[-1] - paid
        loan = Loan.get_client_loan(Loan,loan_id)
        loan.balance = balance
        session.commit()
        self(to_pay,paid,date,balance,loan)

class Documents(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    collateral_id = Column(Integer, ForeignKey('collateral.id'))

    def __init__(self,filename,collateral):
        self.filename = filename
        collateral.files.append(self)
        session.add(self)
        session.commit()


class Collateral(Base):
    __tablename__ = "collateral"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Integer)
    location = Column(String)
    description = Column(String)
    image = Column(String)
    loan_id = Column(Integer, ForeignKey('loan.id'))
    files = relationship("Documents", backref="documents")

    def __init__(self,name,value,location,description,image,loan):
        self.name = name
        self.value = value
        self.location = location
        self.description = description
        self.image = image
        loan.collaterals.append(self)
        session.add(self)
        session.commit()

    def getClientCollateral(self,id):
        return session.query(self).filter_by(id=id).first()

    def deleteClientCollateral(self,id):
        session.query(self).filter_by(id=id).delete()
        session.commit()

class Loan(Base):
    __tablename__ = "loan"
    id = Column(Integer, primary_key=True)
    client_names = Column(String)
    amount_requested = Column(Integer)
    period = Column(Integer)
    previous_loan_performance = Column(String, default="none")
    amount_issued = Column(Integer)
    interest_rate = Column(String)
    loan_type = Column(String)
    interest = Column(Integer)
    principle_interest = Column(Integer)
    balance = Column(Integer)
    status = Column(String, default="pending")

    G_names = Column(String)
    G_dob = Column(DateTime)
    G_telephone = Column(String)
    G_email = Column(String)
    G_residence = Column(String)
    G_work_place = Column(String)
    G_work_place_address = Column(String)
    G_occupation = Column(String)
    G_scanned_ID = Column(String)
    G_LC_letter = Column(String)

    application_date = Column(DateTime, default=datetime.datetime.now())
    approval_date = Column(DateTime)
    rejection_date = Column(DateTime)
    issue_date = Column(DateTime)
    payment_date = Column(DateTime)
    approval_status = Column(Boolean, default=False)
    rejection_reason = Column(String)
    pay = Column(Boolean, default=False)
    loan_committee_verdict = Column(String)
    manager_verdict = Column(String)
    ceo_verdict = Column(String)
    reason = Column(String(500))
    client_id = Column(Integer, ForeignKey('client.id'))
    collaterals = relationship("Collateral", backref="loan")
    kibanja = relationship("LandMortgage", backref="land")
    payments = relationship("Payment", backref="payment")

    def __init__(self,client_names,amount_requested,period,previous_loan_performance,amount_issued,interest_rate,loan_type,interest,
                 principle_interest,balance,G_names,G_dob,G_telephone,G_email,G_residence,G_work_place,
                 G_work_place_address,G_occupation,G_scanned_ID,G_LC_letter,payment_date,client):
        self.client_names = client_names
        self.amount_requested = amount_requested
        self.period = period
        self.previous_loan_performance = previous_loan_performance
        self.amount_issued = amount_issued
        self.interest_rate = interest_rate
        self.loan_type = loan_type
        self.interest = interest
        self.principle_interest = principle_interest
        self.balance = balance

        self.G_names = G_names
        self.G_dob = G_dob
        self.G_telephone = G_telephone
        self.G_email = G_email
        self.G_residence = G_residence
        self.G_work_place = G_work_place
        self.G_work_place_address = G_work_place_address
        self.G_occupation = G_occupation
        self.G_scanned_ID = G_scanned_ID
        self.G_LC_letter = G_LC_letter
        self.payment_date = payment_date

        client.loans.append(self)
        session.add(self)
        session.commit()

    def get_loans(self):
        return session.query(self).all()

    def get_loan_request(self,id):
        client = Client.read_client(Client,id)
        user1 = session.query(User).filter_by(role="manager").first()
        user2 = session.query(User).filter_by(role="ceo").first()
        client_details = {}
        client_details['manager_telephone'] = user1.username
        client_details['ceo_telephone'] = user2.username
        for loan in client.loans:
            if loan.loan_committee_verdict == "forwarded" or loan.status == "issued" or loan.status == "pending" or loan.manager_verdict == "forwarded" or loan.status == "accepted":
                client_details["client_names"] = " ".join([client.surname,client.first_name])
                client_details["client_dob"] = client.dob
                client_details["client_nin"] = client.NIN
                client_details["client_sex"] = client.sex
                client_details["client_telephone"] = client.telephone
                client_details["client_email"] = client.email
                client_details["client_residence"] = client.residence
                client_details["client_work_place"] = client.work_place
                client_details["client_work_place_address"] = client.work_place_address
                client_details["asset_name"] = loan.collaterals[0].name
                client_details["value"] = loan.collaterals[0].value
                client_details["location"] = loan.collaterals[0].location
                client_details["description"] = loan.collaterals[0].description
                client_details["image"] = loan.collaterals[0].image

                files = []
                for file in loan.collaterals[0].files:
                    files.append({'name':file.filename})
                client_details["supporting_files"] = files

                return client_details

    def get_client_loan(self, id):
        return session.query(self).filter_by(id=id).first()

    def get_client_loans(self, client_id):
        return session.query(self).filter_by(client_id=client_id)

    def get_loan_details(self, client_id, status):
        client = Client.read_client(Client,client_id)
        loan_details = {}
        for loan in client.loans:
            if loan.status == status:
                loan_details["asset_name"] = loan.collaterals[0].name
                loan_details["value"] = loan.collaterals[0].value
                loan_details["location"] = loan.collaterals[0].location
                loan_details["description"] = loan.collaterals[0].description
                loan_details["image"] = loan.collaterals[0].image

                files = []
                for file in loan.collaterals[0].files:
                    files.append({'name':file.filename})
                loan_details["supporting_files"] = files

                return loan_details



    def update(self,**kwargs):
        for key,value in kwargs.items():
            pass
        pass

    def accept_loan(self, id):
        loan = session.query(self).filter_by(id=id).first()
        loan.status = "accepted"
        loan.manager_verdict = "false"
        loan.approval_date = datetime.datetime.now()
        loan.approval_status = True
        session.commit()
        session.close()

    def reject_loan(self, id, reason):
        loan = session.query(self).filter_by(id=id).first()
        loan.status = "rejected"
        loan.rejection_reason = reason
        loan.rejection_date = datetime.datetime.now()
        session.commit()
        session.close()

    def issue_payment(self, id):
        loan = session.query(self).filter_by(id=id).first()
        loan.status = "issued"
        loan.issue_date = datetime.datetime.now()
        session.commit()
        session.close()

    def pay_loan(self, client_id):
        client_loans = session.query(self).filter_by(client_id=client_id).all()
        for loan in client_loans:
            if loan.status == "issued":
                return loan

    def check_balance(self, id):
        loan = session.query(self).filter_by(id=id).first()
        for payment in loan.payments:
            if payment.balance == 0:
                client_id = loan.client_id
                loan.status = "complete"
                client = Client.read_client(Client,client_id)
                client.state = False
                session.commit()
                session.close()

    def update_pay(self,id,balance):
        loan = session.query(self).filter_by(id=id).first()
        loan.balance = balance
        loan.pay = True
        session.commit()
        # session.close()

    def check_payments(self, id):
        loan = session.query(self).filter_by(id=id).first()
        payments = []
        for payment in loan.payments:
            payments.append(payment)
        return payments

    def delete_loan(self, id):
        loan = session.query(self).filter_by(id=id).first()
        client = Client.read_client(Client,loan.client_id)
        client.state = False
        del_files = []
        for collateral in loan.collaterals:
            if collateral.image in del_files or loan.G_LC_letter:
                pass
            else:
                def_files.append(loan.G_LC_letter)
                del_files.append(collateral.image)
            for file in collateral.files:
                if file.filename in del_files:
                    pass
                else:
                    del_files.append(file.filename)
                    session.query(Documents).filter_by(id=file.id).delete()
            session.query(Collateral).filter_by(id=collateral.id).delete()
        for file in del_files:
            dir_path = os.path.abspath(os.path.dirname(__file__))
            real_path = dir_path.replace('/models',"")
            file_path = os.path.join( real_path + "/static",file)
            try:
                os.remove(file_path)
            except OSError as e:
                print("Failed with:", e.strerror)
                print("Error code:", e)
            except FileNotFoundError:
                pass
        session.query(self).filter_by(id=id).delete()
        session.commit()
        session.close()

    def forward_manager(self,id,reason):
        loan = session.query(self).filter_by(id=id).first()
        loan.loan_committee_verdict = "forwarded"
        loan.status = "forwarded"
        loan.reason = reason
        session.commit()
        session.close()

    def forward_ceo(self,id,reason):
        loan = session.query(self).filter_by(id=id).first()
        loan.manager_verdict = "forwarded"
        loan.loan_committee_verdict = "false"
        loan.reason = reason
        session.commit()
        session.close()

    def __str__(self):
        return previous_loan_performance

class LoanType(Base):
    __tablename__ = "loan_type"
    id = Column(Integer, primary_key=True)
    loan_name = Column(String)
    interest_rate = Column(Integer)
    description = Column(String)

    def __init__(self, loan_name,interest_rate,description):
        self.loan_name = loan_name
        self.interest_rate = interest_rate
        self.description = description
        session.add(self)
        session.commit()

    def get_loan_types(self):
        return session.query(self).all()

    def update_loan_type(self,id,name,rate,description):
        loan_type = session.query(self).filter_by(id=id).first()
        loan_type.loan_name = name
        loan_type.interest_rate = rate
        loan_type.description = description
        session.commit()
        session.close()

    def delete_loan_type(self,id):
        session.query(self).filter_by(id=id).delete()
        session.commit()
        session.close()

class LoanOfficer(Base):
    __tablename__ = "officer"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    surname = Column(String)
    sex = Column(String)
    email = Column(String)
    telephone = Column(String, unique=True)
    role = Column(String)
    user = relationship("User", uselist=False, backref="users")

    def __init__(self,first_name,surname,sex,email,telephone,role):
        self.first_name = first_name
        self.surname = surname
        self.sex = sex
        self.email = email
        self.telephone = telephone
        self.role = role

        #check if loan officer exits
        loan_officer = session.query(LoanOfficer).filter_by(telephone=telephone).first()
        try:
            session.add(self)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return None


    def get_officers(self):
        officers_list = []
        officers = session.query(self).all()
        for officer in officers:
            if (officer.user.role == "officer" or officer.user.role == "cashier" or officer.user.role == "loan_committee_head" or
                officer.user.role == "loan_committee_member"):
                officers_list.append(officer)
        return officers_list

    def get_officer(self, username):
        officer = session.query(LoanOfficer).filter_by(telephone=username).first()
        officer_details = {
            'id': officer.id,
            'first_name': officer.first_name,
            'surname': officer.surname,
            'telephone_number': officer.telephone,
            'sex': officer.sex,
            'email': officer.email,
            'username': officer.user.username,
            'role': officer.user.role
        }
        return officer_details

    def bus_sum(self):
        summary = {}
        employees = session.query(func.count(self.id)).scalar()
        clients = session.query(func.count(Client.id)).scalar()
        loans = session.query(func.count(Loan.id)).filter(Loan.status == "issued").scalar()
        loan_repo = session.query(Loan).all()
        if loan_repo == []:
            pass
        else:
            amount_issued = []
            principle_interest = []
            for loan in loan_repo:
                if loan.status == "issued":
                    amount_issued.append(loan.amount_issued)
                    principle_interest.append(loan.principle_interest)
            amount_issu = sum(amount_issued)
            interest = sum(principle_interest) - amount_issu
            summary['amount_issued'] = amount_issu
            summary['interest'] = interest

        summary['emps'] = employees
        summary['clients'] = clients
        summary['loans'] = loans

        return summary

    def delete_officer(self, id):
        session.query(self).filter_by(id=id).delete()
        session.commit()
        session.close()



class ClientSchema(ModelSchema):
    class Meta:
        model = Client


class LoanSchema(ModelSchema):
    class Meta:
        model = Loan

class CollateralSchema(ModelSchema):
    class Meta:
        model = Collateral

class PaymentSchema(ModelSchema):
    class Meta:
        model = Payment

class LoanOfficerSchema(ModelSchema):
    class Meta:
        model = LoanOfficer

class LoanTypeSchema(ModelSchema):
    class Meta:
        model = LoanType



#Init Schemas
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

collateral_schema = CollateralSchema()
collaterals_schema = CollateralSchema(many=True)

loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)

payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

loan_officer_schema = LoanOfficerSchema()
loan_officers_schema = LoanOfficerSchema(many=True)

loan_type_schema = LoanTypeSchema()
loan_types_schema = LoanTypeSchema(many=True)
#
# officer = LoanOfficer("Ainembabazi","Law","M","ainelaw@gmail.com","+256772608805","manager")
# username = '+256755640275'
# password = '123'
# role = 'manager'
# user = User(username,password,role,officer)
# user.hash_password(password)
# user.add_officer(officer)

def changeDate(date):
    dt = date.split("-")
    date_time = datetime.datetime(int(dt[0]),int(dt[1]),int(dt[2]))
    return date_time


if __name__ == "__main__":
    try:
        os.remove("data.sqlite")
    except FileNotFoundError:
        pass
    Base.metadata.create_all(bind=engine)
