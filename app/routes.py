from app import app

@app.route('/')
def index():
    return 'Olá, Docker e Flask!'
