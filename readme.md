# Estrutura inicial do projeto
flask-api/
|--.venv/
|--app/
|   |--init__.py
|   |--routes.py
|   |--...
|--.env
|--.gitignore
|--app.py
|--docker-compose.yml
|--Dockerfile
|--requirements.txt
|--readme.md
|--...

## Start do projeto no ambiente docker
docker compose up -d    --> inicia o docker
docker compose down     --> para o docker  
docker compose pull     --> atualiza o conteudo do docker

## Start no projeto fora do docker
.\.venv\Scripts\activate    --> ativa o ambiente virtual
pip install -r requirements.txt --> instala as dependencias do projeto
python app.py   --> roda o projeto