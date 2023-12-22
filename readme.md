## Estrutura inicial do projeto
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
python -m venv .venv                --> criar o embiente virtual (windows)  
.\.venv\Scripts\activate            --> ativa o ambiente virtual  (windows) 
  
python3 -m venv .venv                --> criar o embiente virtual (linux)   
source .venv/bin/activate           --> ativa o ambiente virtual  (linux)  
  
pip install -r requirements.txt     --> instala as dependencias do projeto  
python app.py                       --> rodar o projeto  
deactivate                          --> sair do ambiente virtual

## Atualizar as dependências do projeto (após instalar bibliotecas)
pip freeze > requirements.txt

## Colocar em produção no ambiente linux
pip install gunicorn                        --> Instalar um servidor WSGI  
gunicorn -w 4 -b 0.0.0.0:5000 app:app       --> Rodar o projeto  

## Importando projeto git
sudo git clone git@github.com:developerMallon/flask-api.git
sudo chown -R ti:ti flask-api
cd flask-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

