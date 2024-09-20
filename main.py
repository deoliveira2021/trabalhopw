from flask import Flask, render_template
from database import db
from flask_migrate import Migrate
from credores import bp_credores
from contas import bp_contas
from pagamento import bp_pagamentos

app = Flask(__name__)

conexao = "sqlite:///contaspagar.sqlite"

app.config["SECRET_KEY"] = "123456"
app.config["SQLALCHEMY_DATABASE_URI"] = conexao
app.config["SQLALCHEMY_TRACKMODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(bp_credores, url_prefix='/credores')
app.register_blueprint(bp_contas, url_prefix='/contas')
app.register_blueprint(bp_pagamentos, url_prefix='/pagamentos')


migrate = Migrate(app, db)



@app.route('/')

def index():
    return render_template('index.html')

# app.run()
if __name__ == "__main__":
    app.run(debug=True) #<-- adicionar esta linha