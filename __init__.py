from flask import Flask, render_template, jsonify, request, redirect, make_response
from datetime import timedelta
from flask_jwt_extended import (
    create_access_token,
    decode_token,
    get_jwt_identity,
    JWTManager
)

app = Flask(__name__)

# Configuration du module JWT
app.config["JWT_SECRET_KEY"] = "Ma_clé_secrete"  # Clé secrète
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)  # Expiration du token
jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template("accueil.html")

# 🔹 Route pour afficher le formulaire de connexion
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

# 🔹 Route pour gérer l'authentification et stocker le token dans un cookie
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Simulation d'une base de données
    users = {
        "test": {"password": "test", "role": "user"},
        "admin": {"password": "admin", "role": "admin"},
    }

    user = users.get(username)

    if not user or user["password"] != password:
        return jsonify({"msg": "Mauvais utilisateur ou mot de passe"}), 401

    # Création du token JWT avec le rôle
    access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})

    # Création de la réponse avec le cookie contenant le JWT
    response = make_response(redirect("/protected"))
    response.set_cookie("access_token", access_token, httponly=True)  # Stocke le JWT en cookie HTTPOnly

    return response

# 🔹 Route protégée accessible via le JWT stocké dans un cookie
@app.route("/protected", methods=["GET"])
def protected():
    token = request.cookies.get("access_token")

    if not token:
        return jsonify({"msg": "Acces refuse", "error": "Token manquant"}), 401

    try:
        decoded_token = decode_token(token)  # Décodage manuel du token JWT
        current_user = decoded_token["sub"]  # L'identité est stockée sous "sub"
        return jsonify({"msg": "Acces autorise", "user": current_user}), 200
    except Exception as e:
        return jsonify({"msg": "Acces refuse", "error": str(e)}), 403

# 🔹 Route accessible uniquement aux administrateurs
@app.route("/admin", methods=["GET"])
def admin():
    token = request.cookies.get("access_token")

    if not token:
        return jsonify({"msg": "Acces refuse", "error": "Token manquant"}), 401

    try:
        decoded_token = decode_token(token)  # Décodage du token JWT
        current_user = decoded_token["sub"]  # L'identité est stockée sous "sub"
        role = decoded_token["role"]  # Le rôle de l'utilisateur est stocké sous "role"

        # Vérification si l'utilisateur a le rôle "admin"
        if role != "admin":
            return jsonify({"msg": "Accès interdit", "error": "Administrateur requis"}), 403

        return jsonify({"msg": "Bienvenue, administrateur", "user": current_user}), 200
    except Exception as e:
        return jsonify({"msg": "Acces refuse", "error": str(e)}), 403


if __name__ == "__main__":
    app.run(debug=True)
