from flask import Blueprint
from flask import render_template, request, redirect
from models import Credor, Endereco, Contato, Conta, Pagamento
from database import db
from datetime import datetime
from sqlalchemy import select, insert, delete, update, func
from credores import consultarCredores
from contas import consultarContas


bp_pagamentos = Blueprint("pagamentos", __name__,template_folder="templates")

@bp_pagamentos.route('/cadastrar/<int:contaId>', methods=['GET','POST'])
def cadastrar(contaId):
    if request.method =='POST':
        juros = request.form.get('juros').replace(",", ".").strip(" ")
        juros = juros.replace("R$", "")

        multa = request.form.get('multa').replace(",", ".").strip(" ")
        multa = multa.replace("R$", "")

        total = request.form.get('total').replace(",", ".").strip(" ")
        total = total.replace("R$", "")
        print (juros, multa, total)
        dataPagamento = datetime.strptime(request.form.get('datapagamento'), "%Y-%m-%d")
        contaId = contaId

        qrPagamento = Pagamento.query.filter_by(conta_id = contaId)
        teste = db.session.execute(qrPagamento)
        pagamento = teste.fetchall()
        if(pagamento != []):
            for i in range(len(pagamento)):
                pagamento = list(pagamento[i])
                pagamento[i].data_pagamento = dataPagamento
                pagamento[i].valor = total
                pagamento[i].multa = multa
                pagamento[i].juros = juros

                db.session.add(pagamento[i])
                db.session.commit()
        
    pagamentos = consultarPagamentos()
    credores = consultarCredores()
    contas = consultarContas()
    conta  = Conta.query.get(contaId)
    contexto = {'contas': contas, 
                "credores": credores,
                "pagamentos": pagamentos,
                "conta":conta,
                }
    
    return render_template('cadastrar_pagamentos.html', context=contexto)

@bp_pagamentos.route('/consultar')
def consultarPagamentos():  
    pagamentos = Pagamento.query.all()
    return pagamentos

@bp_pagamentos.route('/editar/<int:contaId>', methods=['GET','POST'])
def editar(contaId):
    conta  = Conta.query.get(contaId)
    if request.method =='POST':
        cnpj = request.form.get('cnpj')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor').replace(",", ".")
        valor = ''.join(valor.split()).replace('R$', '')
        vencimento = datetime.strptime(request.form.get('vencimento'), "%Y-%m-%d")

        conta.credor_cnpj = cnpj
        conta.descriacao  = descricao    
        conta.valor       = valor
        conta.vencimento  = vencimento   

        db.session.add(conta)
        db.session.commit()        

        return redirect('/contas/cadastrar')
    
    pagamentos = consultarPagamentos()
    credores = consultarCredores()
    contas  = consultarContas()
    contexto = {
        "conta": conta,
        "contas": contas,
        "credores": credores,
        "pagamentos": pagamentos
    }
    return render_template('editar_contas.html', context=contexto)

@bp_pagamentos.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
    pagamento = Pagamento.query.get(id)
    if request.method =='POST':
        db.session.delete(conta)
        db.session.commit()
        return redirect('/pagamentos/cadastrar')
    pagamentos = consultarPagamentos()
    contexto = {
        "pagamento": pagamento,
        "pagamentos": pagamentos,
    }   
    return render_template('excluir_pagamentos.html', context=contexto)
