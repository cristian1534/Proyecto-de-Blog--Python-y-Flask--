from flask import Flask, render_template, redirect, request, flash, session, escape, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView



import os

dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

blog = Flask(__name__)
blog.secret_key = 'ctnm1534'
blog.config["SQLALCHEMY_DATABASE_URI"] = dbdir
blog.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(blog)




class Users(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    admin = db.Column(db.Boolean, default=False)


#ADMIN

class ModelView(ModelView):
    def is_accessible(self):
        return True


admin = Admin(blog, name='Algoritmo Python Blog')
admin.add_view(ModelView(Users,db.session))


#ADMIN



class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    texto = db.Column(db.String, nullable=False)


@blog.route("/")
def index():
    posts = Post.query.order_by(Post.fecha.desc()).all()
    return render_template("index.html", posts=posts)

@blog.route("/crear", methods=["POST"])
def crear_post():
    titulo = request.form.get("titulo")
    texto = request.form.get("texto")
    post = Post(titulo=titulo, texto=texto)
    db.session.add(post)
    db.session.commit()
    return redirect("/")

@blog.route('/borrar', methods=['POST'])
def borrar():
    post_id = request.form.get('post_id')
    post = db.session.query(Post).filter(Post.id == post_id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@blog.route('/signup', methods=['GET','POST'])
def signup():
    if request.method =='POST':
        hashed_pw=generate_password_hash(request.form['password'], method='sha256')
        new_user=Users(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        if 'username' in session:
            flash('Debes hacer Logout para Registrar un nuevo Usuario.')

        return redirect('/login')
    return render_template('signup.html')

@blog.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=Users.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            if 'username' in session:
                    flash('{} ya estas en Login'.format(user.username))
                    return redirect('/login')
            else:
                session['username'] = user.username
                flash('{} acabas de iniciar sesion.'.format(user.username))
                return redirect('/home')

        flash('Usuario o Contraseña incorrecta. Por favor intenta nuevamente.')
        return redirect('login')

    return render_template('login.html')

@blog.route('/home')
def home():
    if 'username' in session:

        return redirect('/')


@blog.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        flash('Acabas de cerrar la secion.')

    return redirect('/')


@blog.route('/contacto')
def contacto():
    return render_template("contacto.html")

@blog.route('/cursos')
def cursos():
    return render_template('cursos.html')

@blog.route('/articulos')
def articulos():
    return render_template('articulos.html')

@blog.errorhandler(404)
@blog.route('/control', methods=['POST','GET'])
def control():
    try:
        if request.method == 'POST':
            user = Users.query.filter_by(username=request.form['username']).first()
            if 'username' in session:
                if user.username == 'admin':
                     return redirect('/admin')


            return render_template('/prohibido.html')
        return render_template('/admin.html')

    except:
            return render_template('/not_found.html')

@blog.errorhandler(404)
def not_found(e):
    return render_template('/not_found.html'),404

@blog.errorhandler(403)
def not_found(e):
    return render_template('/prohibido.html'),403




if __name__=="__main__":
    db.create_all()
    blog.run(debug=True, port=5000)