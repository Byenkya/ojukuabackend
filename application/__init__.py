from flask import Flask

# Init App
app = Flask(__name__)
app.debug = True

# Import blueprints
from application.views.Client.client import client
from application.views.Loan.loan import loan
from application.views.officer.officer import officer

app.register_blueprint(client)
app.register_blueprint(loan)
app.register_blueprint(officer)

app.config["SECRET_KEY"] = "XNDKUJDJ84y2h298yy39001hcbc"
