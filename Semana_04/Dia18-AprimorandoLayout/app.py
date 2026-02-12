from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
#pip install flask_wtf / pip install email_validator
app = Flask(__name__)
app.config['SECRET_KEY'] = 'teste123'

class RegisterForm(FlaskForm):
    nome = StringField('Primeiro Nome') 
    sobrenome = StringField('Sobrenome') 
    email = StringField('E-mail') 
    senha = PasswordField('Senha')
    confirmar = PasswordField('Confirmar Senha')
    btn_cadastrar = SubmitField('Cadastrar')

@app.route('/')
def root():
    return "Olá Mundo!"

@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method ==  'POST':
        dado = request.form['name']
        return f'Você enviou: {dado}'
    return '''
        <form method = "POST">
            Nome: <input type="text" name="name">
            <input type="submit" value="Enviar">
        </form>
    '''

@app.route('/template')
def template():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET','POST'])
def Cadastro():
    form = RegisterForm()
    return render_template('cadastro.html', form=form)

if __name__ == '__main__':
    app.run(debug=True,port=5152)