from flask import Blueprint
from flask import render_template, request, redirect
from models import Credor, Endereco, Contato, Conta, Pagamento
from database import db
from datetime import datetime, date
from sqlalchemy import select, insert, delete, update, func
from credores import consultarCredores
from dateutil.relativedelta import relativedelta
from flask_weasyprint import HTML, render_pdf    


bp_contas = Blueprint("contas", __name__,template_folder="templates")

@bp_contas.route('/cadastrar', methods=['GET','POST'])
def cadastrar():
    if request.method =='POST':
        cnpj = request.form.get('cnpj')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor').replace(",", ".")
        vencimento = datetime.strptime(request.form.get('vencimento'), "%Y-%m-%d")

        conta = Conta(descricao=descricao, credor_cnpj=cnpj, valor=valor, vencimento=vencimento)
        db.session.add(conta)
        db.session.commit()
        
    # contas = consultarContas()[0]
    contas = consultarContas()
    # pagamento = consultarContas()[1]
    credores = consultarCredores()
    # contexto = {'contas': contas, "credores": credores, "pagamento": pagamento }
    contexto = {'contas': contas, "credores": credores,}
    
    return render_template('cadastrar_contas.html', context=contexto)

@bp_contas.route('/consultar')
def consultarContas():  
    # sqlContas = select(Conta.descricao, Credor.nome.label("credor"), Conta.valor, Conta.vencimento, Pagamento.valor.label("ValorPago"),Pagamento.multa, Pagamento.juros, Pagamento.data_pagamento, func.sum(Pagamento.valor>0).label("Pago")).where(Credor.cnpj == Conta.credor_cnpj, Conta.id==Pagamento.conta_id)
    # sqlContas = select(Conta.descricao, Credor.nome.label("credor"), Conta.valor, Conta.vencimento)
    # contas = db.session.execute(sqlContas).all()

    contas = Conta.query.all()
    dataAtual = date.today()
    for conta in contas:
        qrPagamento = Pagamento.query.filter_by(conta_id = conta.id)
        teste = db.session.execute(qrPagamento)
        pagamento = teste.fetchall()

        atraso = abs(relativedelta(dataAtual,conta.vencimento))
        diasAtraso = atraso.days
        if(dataAtual > conta.vencimento):
            multa = conta.valor*2/100 # a multa padrão por atraso é de 2% sobre o valor principal
            juros = conta.valor*(0.01/30)*diasAtraso
        else:
            multa = 0.00
            juros = 0.00

        valor = conta.valor + juros + multa
        # print("Dias:", diasAtraso, "Multa:", multa, "Juros:",juros)

        if  len(pagamento) <= 0 :
            valor = 0.00
            pagamento = Pagamento(conta.id, valor, multa, juros)
            db.session.add(pagamento)
            db.session.commit()

        else:
            for i in range(len(pagamento)):
                pagamento = list(pagamento[i])                   
                if pagamento[i].conta_id == conta.id:
                    pagamento[i].juros = juros
                    pagamento[i].multa = multa
                    if pagamento[i].valor == None:
                        pagamento[i].valor = 0.00
                
                db.session.add(pagamento[i])
                db.session.commit()

    return contas

@bp_contas.route('/editar/<int:contaId>', methods=['GET','POST'])
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
    
    contas = consultarContas()
    credores = consultarCredores()
    contexto = {
        "conta": conta,
        "contas": contas,
        "credores": credores
    }
    return render_template('editar_contas.html', context=contexto)

@bp_contas.route('/delete/<int:contaId>', methods=['GET','POST'])
def delete(contaId):
    conta = Conta.query.get(contaId)
    if request.method =='POST':
        db.session.delete(conta)
        db.session.commit()
        return redirect('/contas/cadastrar')
    contas = consultarContas()
    contexto = {
        "conta": conta,
        "contas": contas,
    }   
    return render_template('excluir_contas.html', context=contexto)



@bp_contas.route('/relatoriotodas')
def imprimirTodas():
    titulo = "RELATÓRIO DE TODAS AS CONTAS"
    contas = Conta.query.all()
    contexto = {
        "titulo": titulo,
        "contas": contas
    }
    html = render_template('relatoriocontas.html', contexto = contexto)

    return render_pdf(HTML(string=html))

@bp_contas.route('/relatoriopagas')
def imprimirPagas():
    pagamento = Pagamento.query.all()
    titulo = "RELATÓRIO DE TODAS AS CONTAS PAGAS"
    contas = []
    for i in range(len(pagamento)):
        conta = Conta.query.get(pagamento[i].conta_id)
        if (pagamento[i].valor >= conta.valor):
            contas.append(conta)

    contexto = {
        "titulo": titulo,
        "contas": contas
    }            
    html = render_template('relatoriocontas.html', contexto = contexto)
    return render_pdf(HTML(string=html))


@bp_contas.route('/relatoriovencidas')
def imprimirVencidas():
    titulo = "RELATÓRIO DE TODAS AS CONTAS VENCIDAS"
    dataAtual = date.today()

    sqlContas = select(Conta, Pagamento).where(Conta.vencimento < dataAtual).where(Pagamento.valor < Conta.valor).where(Pagamento.conta_id==Conta.id)
    qrContas  = db.session.execute(sqlContas)
    novacontas = qrContas.fetchall()
    print(novacontas)
    
    contas = []
    for i in range((len(novacontas))):
        conta = list(novacontas[i])
        contas.append(conta[i])

    contexto = {
        "titulo": titulo,
        "contas": contas
    }            
    html = render_template('relatoriocontas.html', contexto = contexto)
    return render_pdf(HTML(string=html))


@bp_contas.route('/relatorioavencer')
def imprimirVencer():
    titulo = "RELATÓRIO DE TODAS AS CONTAS A VENCER"
    dataAtual = date.today()
    # sqlContas = select(Conta, Pagamento).where(Conta.vencimento >= dataAtual).where(Pagamento.valor > Conta.valor)
    sqlContas = select(Conta).where(Conta.vencimento >= dataAtual) #.where(db.or_(Conta.id == Pagamento.conta_id, Conta.id !=Pagamento.conta_id))
    qrContas  = db.session.execute(sqlContas)
    novacontas = qrContas.fetchall() 

    print(novacontas)
    contas = []
    for i in range(len(novacontas)):
        conta = list(novacontas[i])
        contas.append(conta[i])

    contexto = {
        "titulo": titulo,
        "contas": contas
    }            
    html = render_template('relatoriocontas.html', contexto = contexto)
    return render_pdf(HTML(string=html))