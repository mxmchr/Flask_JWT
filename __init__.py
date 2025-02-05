from flask import Flask, render_template, jsonify, request, make_response
from datetime import timedelta
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
    set_access_cookies,
    unset_jwt_cookies
)

app = Flask(__name__)

# Configuration du module JWT
app.config["JWT_SECRET_KEY"] = "Ma_clé_secrete"  # Ma clé secrète
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Utilisation des cookies pour stocker le token
app.config["JWT_COOKIE_SECURE"] = False  # Doit être True en production (HTTPS)
app.config["JWT_COOKIE_HTTPONLY"] = True  # Empêche l'accès au cookie via JavaScript
app.config["JWT_COOKIE_SAMESITE"] = "Lax"  # Évite certaines attaques CSRF

jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template('accueil.html')

# Création d'une route qui vérifie l'utilisateur et stocke le token dans un cookie
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

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

    # Création de la réponse avec un cookie contenant le token
    response = jsonify({"msg": "Connexion réussie"})
    set_access_cookies(response, access_token)  # Stocke le token dans un cookie

    return response

# Déconnexion : suppression du cookie
@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "Déconnexion réussie"})
    unset_jwt_cookies(response)  # Supprime les cookies contenant le token
    return response

# Route protégée accessible uniquement via le cookie JWT
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Route accessible uniquement aux administrateurs
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg": "Accès refusé : administrateur requis"}), 403

    return jsonify({"msg": "Bienvenue, administrateur"}), 200

if __name__ == "__main__":
    app.run(debug=True)
