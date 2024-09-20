from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, BooleanField, IntegerField, FloatField, PasswordField,DateField
from wtforms.validators import DataRequired, Length, Email
# from wtforms.meta import DefaultMeta


from models import Credor, Contato, Endereco, Conta, Pagamento
from database import db

## Estrutura do fomulário de contatos
class ContatoForm(FlaskForm):
    nome = StringField("nome",validators=[DataRequired(), Length(max=150)])
    telefone = StringField("telefone",validators=[DataRequired()])
    email = StringField("email",validators=[DataRequired(), Email()])
    whatsapp = StringField("whatsapp",validators=[DataRequired()])


## Estrutura da tabela de endereço
class EnderecoForm(FlaskForm):
    cep = StringField("CEP",validators=[DataRequired(), Length(max=8)])
    logradouro = StringField("logradouro",validators=[DataRequired()])
    numero = StringField("numero")
    complemento = StringField("complemento")
    cidade = StringField("cidade",validators=[DataRequired()])
    uf = StringField("uf",validators=[DataRequired()])

    
## Estrutura da tabela de credores
class CredorForm(FlaskForm):
  cnpj = StringField("CNPJ",validators=[DataRequired(), Length(max=150)])
  nome = StringField("Nome",validators=[DataRequired()])
       

## Estrutura da tabela de contas a pagar
class ContaForm(FlaskForm):
  descricao = StringField("descricao",validators=[DataRequired()])
  credor_cnpj = StringField("credor_cnpj",validators=[DataRequired()])
  valor = FloatField("valor", validators=[DataRequired()])
  vencimento = DateField("vencimento", validators=[DataRequired()])
    
class PagamentoForm(FlaskForm):

  # data_pagamento = DateField("data_pagamento", validators=[DataRequired()])
  data_pagamento = DateField("data_pagamento")
  valor = FloatField("valor", validators=[DataRequired()], default=0.0)
  multa = FloatField("multa", validators=[DataRequired()], default=0.0)
  juros = FloatField("juros", validators=[DataRequired()], default= 0.0)
    