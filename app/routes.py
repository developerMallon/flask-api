from app import app
from flask import Flask, request
import jwt
from dotenv import dotenv_values

# Carrega os valores do .env
config = dotenv_values(".env")

@app.route('/')
def index():
    return 'Api flask rodando.'

@app.route('/token', methods=['POST'])
def token():
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
            payload = jwt.decode(token, config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return 'Token expirado. Faça login novamente.'
        except jwt.InvalidTokenError:
            return 'Token inválido. Faça login novamente.'

    # Agora você pode usar o token conforme necessário
    return f'Token validado com sucesso: {token}', 200
