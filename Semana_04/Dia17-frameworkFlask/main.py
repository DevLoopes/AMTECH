from flask import Flask
app = Flask(__name__)

# Localizar de onde vem as ROUTES
from views import * 

if __name__ == "__main__": # Diz para o comparador do programa que se for a aplicação chamando executa a aplicação
    app.run()