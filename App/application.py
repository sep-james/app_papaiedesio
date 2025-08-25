from flask import Flask, render_template , request , jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_required, login_user, LoginManager, current_user,logout_user

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///Reciclagem.db'

login_manager = LoginManager()
db = SQLAlchemy(application)
login_manager.init_app(application)
login_manager.login_view = "login"
CORS(application)

class Coletor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    senha = db.Column(db.String(120), nullable=False)
    coleta_aceita = db.Column(db.Boolean, default=False)
    avaliacao = db.Column(db.Float)
    historico = db.relationship('Historico', backref='coletor', lazy=True)


    
class Doador(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120))
    senha = db.Column(db.String(120), unique = True, nullable=False)
    historico = db.relationship('Historico', backref='Doador', lazy=True)
    EntregaRealizada = db.Column(db.Boolean, default=False)
    avaliacao = db.Column(db.Float)

class Lixo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=False)
    tipo = db.Column(db.String(30))
    peso = db.Column(db.Float)
    unidade = db.Column(db.String(10))
    quantidade = db.Column(db.Integer)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


    coletor = db.relationship('Coletor', backref='lixos')
    doador = db.relationship('Doador', backref='lixos')
    entregue = db.Column(db.Boolean, default=False)



class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)

    coleta = db.Column(db.Boolean, default=False, nullable=False)
    doacao = db.Column(db.Boolean, default=False, nullable=False)

    coletor = db.relationship('Coletor', backref='historicos', lazy=True)
    doador = db.relationship('Doador', backref='historicos', lazy=True)


class Entrega(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    localinicial = db.Column(db.String(120))
    localfinal = db.Column(db.String(120))

    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)

    coletor = db.relationship('Coletor', backref='entregas', lazy=True)
    doador = db.relationship('Doador', backref='entregas', lazy=True)

    historico = db.Column(db.String(120))

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    mensagem = db.Column(db.String(255), nullable=False)
    visualizada = db.Column(db.Boolean, default=False)

    doador = db.relationship('Doador', backref='notificacoes', lazy=True)
    coletor = db.relationship('Coletor', backref='notificacoes', lazy=True)



@login_manager.user_loader
def load_user(user_id):
    user_type = session.get("user_type")
    if user_type == "coletor":
        return Coletor.query.get(int(user_id))
    elif user_type == "doador":
        return Doador.query.get(int(user_id))
    else:
        return None    


@application.route('/', methods=["GET"])
def init():
    return render_template("tutorial.html")

@application.route('/login', methods=["GET"])
def login_page():
    return render_template("login.html")

    
@application.route('/cadastro', methods=["POST"])
def cadastro_usuario():
    data = request.json
    user_type = session.get("user_type")
    if "nome" in data and "email" in data and "senha" in data:
        if user_type == "doador":
            doador = Doador(nome=data["nome"],email=data["email"],senha=data["senha"])
            db.session.add(doador)
            db.session.commit()
            return jsonify({"message": "Cadastro de doador realizado com sucesso"})
        
        elif user_type == "coletor":
            coletor = Coletor(nome=data["nome"],email=data["email"],senha=data["senha"])
            db.session.add(coletor)
            db.session.commit()
            return jsonify({"message": "Cadastro de coletor realizado com sucesso"})
        
        else:
            return jsonify({"message": "user_type invalido"}),400
    else:     
        return jsonify({"message": "erro ao fazer o cadastro"}),400


@application.route('/login/Doador', methods=["POST"])
def loginDoador():
    data = request.json
    user = Doador.query.filter_by(nome=data["nome"]).first()

    if user and data.get("senha") == user.senha and data.get("email") == user.email:
        login_user(user)
        session["user_type"] = "doador"
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "avaliacao": user.avaliacao
            }
        })    
    return jsonify({"message": "Credenciais inválidas"}), 401


@application.route('/login/Coletor', methods=["POST"])
def loginColetor():
    data = request.json
    user = Coletor.query.filter_by(nome=data["nome"]).first()

    if user and data.get("senha") == user.senha and data.get("email") == user.email:
        login_user(user)
        session["user_type"] = "coletor"
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "avaliacao": user.avaliacao
            }
        })    
    return jsonify({ "message": "Credenciais inválidas"}), 401


@application.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    session.pop("user_type", None)
    return jsonify({"message": "Logout realizado com sucesso"})

# Nesse ponto eu não quero mais viver, se vc for um usuario e estiver bisbilhotando o codigo, saiba que isso foi feito por uma criança, e foi trabalho escravo, if puder denuncie ao 190, ta feliz agora
#LULA_ladrao2025_100%atualizado!!!
#Perdi minha partida de bomba patche, ta feliz edesio neto, Rumbora vasco!!!

@application.route('/doador/coletor/criar', methods=["POST"])
@login_required
def criar_coleta():
    if session.get("user_type") != "doador":
        return jsonify({"message": "Apenas doadores podem criar coletas"}), 403
    
    data = request.json
    
    campos = ["tipo", "peso","latitude","longitude"]
    for campo in campos:
        if campo not in data or data[campo] == None:
            return jsonify({"message": f"campo obrigatorio faltando: {campo}"}),400
        
    unidade = data.get("unidade")
    quantidade = data.get("quantidade")

    if not unidade and not quantidade:
        return jsonify({"message": "É necessário informar unidade ou quantidade"}), 400    

    peso = float(data["peso"])    
    if peso <= 0:
        return jsonify({"message": "o peso deve ser maior que zero"}),400


    nova_coleta = Lixo(
        doador_id = current_user.id,
        tipo = data["tipo"],
        peso = peso,
        unidade=unidade,
        quantidade=quantidade,
        latitude=data["latitude"],
        longitude=data["longitude"])

    db.session.add(nova_coleta)
    db.session.commit()
    return jsonify({"message": "Coleta criada com sucesso", "coleta_id": nova_coleta.id})



@application.route('/coletas/disponiveis', methods=["GET"])
@login_required
def listar_coletas_disponiveis():
    if session.get("user_type") != "coletor":
        return jsonify({"message": "apenas coletores podem acessar"}),403

    coletas = Lixo.query.filter_by(coletor_id=None).all()
    resultado = []
    for coleta in coletas:
        resultado.append({
            "id": coleta.id,
            "tipo": coleta.tipo,
            "peso": coleta.peso,
            "unidade": coleta.unidade,
            "quantidade": coleta.quantidade,
            "latitude": coleta.latitude,
            "longitude": coleta.longitude,
            "doador_id": coleta.doador_id
        })    
    return jsonify({"coletas_disponiveis": resultado})

@application.route('/coleta/aceita/<int:lixo_id>', methods=["POST"])
@login_required
def ColetorPedidoAceito(lixo_id):
    if session.get("user_type") != "coletor":
        return jsonify ({"message": "apenas coletores podem aceitar coletas"}), 403
    
    coleta = Lixo.query.get(lixo_id)
    data = request.json
   

    if not coleta:
        return jsonify({"message": "coleta não encontrado"}),404
    
    if coleta.coletor_id != None:
        return jsonify({"message": "coleta já aceita"}), 400
    
    coleta.coletor_id = current_user.id
    db.session.commit()

    notificacao = Notificacao(doador_id=coleta.doador_id,mensagem=f"Um coletor aceitou sua coleta do tipo {coleta.tipo}.")


    db.session.add(notificacao)
    db.session.commit()
    return jsonify({"message": "Coleta aceita com sucesso", "coleta_id": coleta.id})


# vai se ferrar fortaleza, em vez de tirar minha tristeza faz é aumentar. Agora eu também sou é mengão
#para o meu eu de amanha: "por hoje esta bom", trabalhe em uma rota de notifação,para que apos serem visualizadas as notificações sumam
#todas as rotas que estão abaixo desses comentarios ainda devem modificados, pois ainda não estão prontos


@application.route('/coleta/realizada/<int:coleta_id>', methods=["POST"])
@login_required
def ColetaRealizada(coleta_id):
    if session.get("user_type") != "doador":
        return jsonify({"message":"apenas doadores podem finalizar a coleta "}),403
    
    coleta = Lixo.query.get(coleta_id)
    if not coleta:
        return jsonify({"message":"coleta não encontrada"}),404
    if coleta.doador_id != current_user.id:
        return jsonify({"message":"doador sem permissão para finalizar a coleta"}),403
    if coleta.coletor_id is None:
        return jsonify({"message":"a coleta ainda não foi aceita"}),400
    if coleta.entregue:
        return jsonify({"message": "a coleta já foi realizada"})

    historico = Historico(
        coletor_id = coleta.coletor_id,
        doador_id = coleta.doador_id,
        coleta = True,
        doacao = True
    )
    db.session.add(historico)
    coleta.entregue = True 
    db.session.commit()
    return jsonify({"message":"coleta finalizada com sucesso"})


@application.route('/notificacoes',methods=["GET"])
@login_required
def listar_notificacoes():
    user_type = session.get("user_type")
    if user_type == "doador":
        notificacoes = Notificacao.query.filter_by(doador_id=current_user.id,visualizada=False).all()
    elif user_type == "coletor":
        notificacoes = Notificacao.query.filter_by(coletor_id=current_user.id,visualizada=False).all()
    else:
        return jsonify({"message": "tipo de usuario invalido"}),400
    
    lista_notificacoes = []
    for notificacao in notificacoes:
        lista_notificacoes.append({
            "id": notificacao.id,
            "mensagem": notificacao.mensagem,
            "visualizada": notificacao.visualizada   
        })
    return jsonify({"notificações": lista_notificacoes})    


@application.route('/notificacoes/deletar/<int:notificacao_id>',methods=["DELETE"])
@login_required
def apagar_notificacao(notificacao_id):
    notificacao = Notificacao.query.get(notificacao_id)

    notificacao.visualizada = True
    db.session.delete(notificacao)
    db.session.commit()
    return jsonify({"message": "notificacao deletada"})


@application.route('/notificacoes/visualizar/<int:notificacao_id>',methods=["PUT"])
@login_required
def visualizar_notificacao(notificacao_id):
    notificacao = Notificacao.query.get(notificacao_id)
    if not notificacao:
        return jsonify({"message": "notificacoes não encontradas"}),404
    notificacao.visualizada = True
    db.session.commit()
    return jsonify({"message": "mensagem visualizada"})


#historico,avalaização,ranque e chat

@application.route('/historico/lista', methods=["GET"])
@login_required
def pegar_historico():
    user_type = session.get("user_type")
    if user_type == "coletor":
        historico = Historico.query.filter_by(coletor_id=current_user.id)
    elif user_type == "doador":
        historico = Historico.query.filter_by(doador_id=current_user.id)
    else:
        return jsonify({"message": "tipo de usuario invalido"}),400

    lista_historico = []
    for item_historico in historico:
        lista_historico.append({
             "id": item_historico.id,
             "coleta": item_historico.coleta,
             "doação": item_historico.doacao
        })
    return jsonify({"historico": lista_historico})

@application.route('/historico/delete/<int:historico_id>')
@login_required
def deletar_historico(historico_id):
    user_type = session.get("user_type")
    if user_type != "doador" and user_type != "coletor" :
        return jsonify({"message": "tipo de usuario invalido"}),400
    
    historico = Historico.query.get(historico_id)
    if not historico: 
        return jsonify({"message": "historico não encontrado"}),404

    if user_type == "doador" and historico.doador_id != current_user.id:
        return jsonify({"message": "Você não tem permissão para deletar esse histórico"}), 403
    if user_type == "coletor" and historico.coletor_id != current_user.id:
        return jsonify({"message": "Você não tem permissão para deletar esse histórico"}), 403
    
    db.session.delete(historico)
    db.session.commit()
    return jsonify({"message": "historico deletado com sucesso"})


@application.route('/historico/delete/item/<int:historico_id>')
@login_required
def deletar_por_item(historico_id):
    historico_item = Historico.query.get(historico_id)
    
    if historico_item.doador_id != current_user.id and historico_item.coletor_id != current_user.id:
        return jsonify({"message": "Você não tem permissão para deletar esse item"}), 403
    
    db.session.delete(historico_item)
    db.session.commit()
    return jsonify({"message": "item deletado com sucesso"})

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)


# @application.route('/login/usuario/chat', methods=["POST"])
# @login_required
# def Chat():

    

# @application.route('/login/usuario/avaliar', methods=["POST"])
# @login_required
# def AvaliarUsuario():



   



