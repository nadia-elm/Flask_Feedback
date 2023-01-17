from flask import Flask, render_template, redirect, session, flash,request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User,db, Feedback
from forms import RegisterForm, LoginForm, FeedBackForm
# from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:secret@localhost:5432/feedback'

# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///Feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "SECRET"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
    # if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password,email, first_name, last_name )
        # db.session.add(new_user)
        db.session.commit()
        
        session['username'] = new_user.username

        flash('Welcome ! you have registered successfully ', 'success')

        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form = form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {user.username}', 'primary')
            session['username'] = user.username
            return redirect(f'users/{username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form = form)




@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        flash("You have successfully logged out !", 'primary')
        return redirect('/')




@app.route('/users/<username>')
def user_page(username):
    if 'username' in session:
        user= User.query.get_or_404(username)
        # feedbacks = Feedback.query.filter(user.username == Feedback.username )
        return render_template('users_details.html', user =user)

    flash('Please log in first !', 'primary')
    return redirect('/login')


@app.route('/users/<username>/feedback/add',methods=['GET', 'POST'])
def add_feedback(username):
   
    if 'username'  not in session or username  != session['username']:
        flash('please login first','info')
        return redirect('/login')

    form = FeedBackForm()

    if request.method == 'POST' and form.validate():
            title = form.title.data
            content = form.content.data
            feedback = Feedback(title =title, content = content, username = username)
            db.session.add(feedback)
            db.session.commit()

            return redirect(f"/users/{feedback.username}")
    else:
        return render_template('add_feedback.html', form =form )



@app.route('/feedback/<feedback_id>/edit', methods= ['GET', 'POST'])
def edit_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username'  not in session or  feedback.username  != session['username']:
        flash('please login first','info')
        return redirect('/login')

   

    form = FeedBackForm()
    if request.method == 'POST' and form.validate():

    # if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")


    return render_template('edit.html',feedback = feedback,form = form)


    
@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username'  not in session or  feedback.username  != session['username']:
        flash('please login first','info')
        return redirect('/login')
    db.session.delete(feedback)
    db.session.commit()
    flash('FeedBack Deleted !', 'success')
    return redirect(f"/users/{feedback.username}")


@app.route('/users/<username>/delete', methods =['POST'])
def delete_user(username):
    if 'username'  not in session or  username  != session['username']:
        flash('please login first','info')
        return redirect('/login')

    session.pop('username')

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    flash('account deleted successfully', 'danger')
    return redirect('/')

   





