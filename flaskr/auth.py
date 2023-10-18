import functools

#Funciones propias de flask que ayudan al inicio de sesión
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

#Modulo que cifra la contraseña al enviarla a la base de datos y la descifra al invocarla
from werkzeug.security import check_password_hash, generate_password_hash

#importamos de flask db la función que crea la conexión con sqlite
from flaskr.db import get_db

#variable que almacena BP, 'auth' es este archivo, name = modulo principal, url_prefix = archivo base
bp = Blueprint('auth', __name__, url_prefix='/auth')

#Creamos la dirección donde se va a guardar, Methods son los soportados
@bp.route('/register', methods=('GET', 'POST')) #Get para configración, POST para transferencia de información
def register(): 
    if request.method == 'POST':
        username = request.form['username'] #Request.form = Pide un usuario
        password = request.form['password'] #Request.form = Pide una contraseña
        db = get_db() #Conecta a la base de datos
        error = None

        #Si no ingresan usuario o password provoca error 
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try: #Si no hay errores se pasa los datos a la base de datos
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    #Con generate_pasword_hash se cifran las contraseñas
                    (username, generate_password_hash(password)),
                )
                db.commit() #Se suben los cambios a la db
            except db.IntegrityError:
                error = f"User {username} is already registered." #Error si esta registrado el user
            else:
                #Si no falla se pasa al login para iniciar sesión
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

#Se crea la nueva vista que llevará al login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'] #Se pide usuario
        password = request.form['password'] #Se pide contraseña
        db = get_db() #Se conecta a la base de datos
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,) #Consulta si xisten los datos
        ).fetchone() 

        if user is None:
            error = 'Incorrect username.'
            #check_password_hash compara el hash enviado con el que se creo en el register
        elif not check_password_hash(user['password'], password): 
            error = 'Incorrect password.' 

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            #Si todo esta bien redireciona a la vista hello
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#Decorador para hacer funcionar el blog
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#Salir de la sesión
@bp.route('/logout')
def logout():
    session.clear()
    #redireciona a la primera vista del Login
    return redirect(url_for('auth.login'))

#Volver a iniciar sesión
def login_required(view):
    @functools.wraps(view)#Functools.wraps guarda la view
    def wrapped_view(**kwargs):
        if g.user is None:
            #Nos envia al login
            return redirect(url_for('auth.login'))
        #Si ingresa se redirige a donde estaba
        return view(**kwargs)

    return wrapped_view