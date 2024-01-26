from flask import Flask, request, jsonify
from loginManager import login_manager
from flask_login import login_user, current_user, logout_user,login_required

from models.user import User

from database import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({'message': 'Usuario autenticado'})
        

    return jsonify({'message': 'Credenciais inválidas'}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout realizado'})

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Cadastro realizado.'})

    return jsonify({'message': 'Dados inválidas'}), 401

@app.route("/user/<int:id>",methods={"GET"})
def get_user(id):
    user = User.query.get(id)

    if user:
        return {'username': user.username}
    
    return jsonify({'message': 'Usuário não encontrado.'}), 404

@app.route("/user/<int:id>",methods={"PUT"})
def update_user(id):
    user = User.query.get(id)
    data = request.json

    if user:
        user.password = data.get('password')
        db.session.commit()

        return jsonify({'message': 'Usuário atualizado.'})
    
    return jsonify({'message': 'Usuário não encontrado.'}), 404

@app.route('/user/<int:id>', methods=["DELETE"])
@login_required
def delete_user(id):
  user = User.query.get(id)

  if id == current_user.id:
    return jsonify({"message": "Deleção não permitida"}), 403

  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuário {id} deletado com sucesso"})
  
  return jsonify({"message": "Usuario não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)