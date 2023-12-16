from app import app
from flask import Flask, request
import jwt
from dotenv import dotenv_values
from functools import wraps

# Carrega os valores do .env
config = dotenv_values(".env")

# Decorator para validar o token
def verify_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Obtém o token do cabeçalho Authorization
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return 'Token não fornecido', 401

        # Verifica se o cabeçalho começa com 'Bearer '
        if not authorization_header.startswith('Bearer '):
            return 'Formato de token inválido', 401

        # Extrai o token removendo 'Bearer ' do início
        token = authorization_header.split(' ')[1]

        if token:
            try:
                payload = jwt.decode(
                    token, config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return 'Token expirado. Faça login novamente.', 401
            except jwt.InvalidTokenError:
                return 'Token inválido. Faça login novamente.', 401

        return f(*args, **kwargs)

    return wrapper

@app.route('/')
def index():
    return 'Api flask rodando.'

@app.route('/token', methods=['POST'])
@verify_token
def token():
    return f'Token validado com sucesso: {token}', 200

@app.route('/dias-uteis/<mes>', methods=['POST'])
@verify_token
def dias_uteis(mes):
    return f"Dias úteis do mes {mes}"