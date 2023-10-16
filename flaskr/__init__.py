import os 

from flask import Flask

#Se invoca a los módulos a usar

#FABRICA DE APLICACIONES (Despega todo)

def create_app(test_config = None):
    #Configuración de la app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY= 'dev',
        DATABASE= os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #Se importan las diferentes funciones 

    from . import db #Despega la db
    db.init_app(app)
    
    from . import auth #La vista de authentification
    app.register_blueprint(auth.bp)

    from . import blog #Blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    if test_config is None:
        #Si existe la función se debe de cargar aunque no se este probando
        app.config.from_pyfile("config.py", silent=True)
    else:
        #Si pasa, se carga la configuración
        app.config.from_mapping(test_config)
    
    #Comprobar que la carpeta exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    #Se regresa la vista
    @app.route('/hello')
    def hello():
        return "Hello word"
    
    return app