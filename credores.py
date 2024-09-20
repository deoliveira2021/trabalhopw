from flask import Blueprint
from flask import render_template, request, redirect, url_for
from models import Credor, Endereco, Contato
from database import db
from forms import CredorForm, ContatoForm, EnderecoForm

bp_credores = Blueprint("credores", __name__,template_folder="templates")

@bp_credores.route('/cadastrar', methods=['GET','POST'])
def cadastrar():
    if request.method =='POST':
        cnpj = request.form.get('cnpj')
        nome = request.form.get('nome')
        
        #dados do contato
        nomecontato = request.form.get('nomecontato')
        telefone = request.form.get('telefone')
        whatsapp = request.form.get('whatsapp')
        email = request.form.get('email')
        #dados do endereço
        cep = request.form.get('cep')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        cidade = request.form.get('cidade')
        uf = request.form.get('uf')


        #------------ Instancia os objetos Endereco e Contato Credor ------
        endereco = Endereco(cep,logradouro,numero,complemento,cidade,uf)
        contato = Contato(nomecontato,telefone,email,whatsapp)

        #Verifica se o CNPJ não existe no banco
        localizarCredor = Credor.query.get(cnpj)
        if (localizarCredor==None):
            credor = Credor(cnpj, nome, cep)
            credor.contato = contato

            #Verifica se o CEP já está cadastrado na tabela de endereços
            if(Endereco.query.get(cep)==None):
                credor.endereco = endereco
            else:
                credor.ender_cep = cep

            db.session.add(credor)
            db.session.commit()

            return redirect('/credores/cadastrar')
        
    # if request.method =='GET':
    #     return render_template('cadastrar_credores.html', contexto=credores)

    credores = consultarCredores()
    contexto = {
        "credores": credores
    }
    # return render_template('cadastrar_credores.html', context=contexto)
    return render_template('cadastrar_credores.html', contexto=contexto)

        # return redirect('/credores/consultar')
@bp_credores.route('/consultar')
def consultarCredores():
     credores = Credor.query.all()
     return credores

@bp_credores.route('/editar/<string:cnpj>', methods=['GET','POST'])
def editar(cnpj):
    credor = Credor.query.get(cnpj)
    contato = Contato.query.get(credor.contato_id)
    endereco = Endereco.query.get(credor.ender_cep)
    
    if request.method =='POST':
        nome = request.form.get('nome')

        #Atualizar informações de endereço
        cep = request.form.get('cep')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        cidade = request.form.get('cidade')
        uf = request.form.get('uf')

        #Se o cep for o mesmo cep inicialmente recuperado, vai atualizar os outros dados, senão, vai adicionar novo endereço no banco
        if(cep == endereco.cep):
            endereco.logradouro = logradouro
            endereco.numero = numero
            endereco.complemento = complemento
            endereco.cidade = cidade
            endereco.uf = uf
        else:
            #atualiza o cep no credor
            credor.ender_cep = cep
            #instancia o objeto endereco, com os novos dados
            endereco = Endereco(cep,logradouro,numero,complemento,cidade,uf)
              
        #informações de contato
        nomecontato = request.form.get('nomecontato')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        whatsapp = request.form.get('whatsapp')

        # #atualiza dados do contato
        contato.nome = nomecontato
        contato.telefone = telefone
        contato.email = email
        contato.whatsapp = whatsapp

        #atualiza o nome do credor
        credor.nome = nome
        credor.contato = contato
        credor.endereco = endereco

        #salva no banco os dados
        db.session.add(credor)
        db.session.commit()
        return redirect('/credores/cadastrar')
    
    ## Seleciona todos os credores para renderizar a tabela com os credores.   
    credores = consultarCredores()
    contexto = {"credor": credor, "credores": credores}
    return render_template('editar_credores.html', contexto=contexto)


@bp_credores.route('/delete/<string:cnpj>', methods=['GET','POST'])
def delete(cnpj):
    credor = Credor.query.get(cnpj)
    if request.method =='POST':
        db.session.delete(credor)
        db.session.commit()
        return redirect('/credores/cadastrar')
    
    credores = consultarCredores()
    contexto = {"credor": credor, "credores": credores}

    return render_template('excluir_credores.html', contexto=contexto)
