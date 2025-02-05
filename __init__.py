from flask import Flask, render_template, jsonify, request, redirect, make_response
from datetime import timedelta
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    JWTManager,
)

app = Flask(__name__)

# Configuration du module JWT
app.config["JWT_SECRET_KEY"] = "Ma_clé_secrete"  # Ma clé secrète
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return render_template('accueil.html')

# 🔹 Route pour afficher le formulaire de connexion
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

# 🔹 Route pour traiter la connexion et stocker le token dans un cookie
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Simulation d'une base de données avec des rôles
    users = {
        "test": {"password": "test", "role": "user"},
        "admin": {"password": "admin", "role": "admin"},
    }

    user = users.get(username)

    if not user or user["password"] != password:
        return jsonify({"msg": "Mauvais utilisateur ou mot de passe"}), 401

    # Création du token avec le rôle
    access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})

    # Création de la réponse avec un cookie contenant le JWT
    response = make_response(redirect("/protected"))  # Redirige après connexion
    response.set_cookie("access_token", access_token, httponly=True)  # Stocke le token dans un cookie HTTPOnly

    return response

# 🔹 Route protégée accessible à tout utilisateur authentifié
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# 🔹 Route accessible uniquement aux administrateurs
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg": "Accès refusé : administrateur requis"}), 403

    return jsonify({"msg": "Bienvenue, administrateur"}), 200

if __name__ == "__main__":
    app.run(debug=True)
