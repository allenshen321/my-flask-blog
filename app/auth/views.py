from flask import render_template, redirect, url_for, flash, request
from flask.ext.login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, ChangePassword
from . import auth
from ..models import User
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data
                    )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认邮件', 'auth/confirm', token=token, user=user)
        flash('确认邮件已经发送到您的邮箱,请及时确认!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('你之前已经确认过了,可以正常访问!')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经完成确认,谢谢!')
    else:
        flash('确认网址无效或者已过期!')
    return redirect(url_for('main.index'))


@auth.before_request
def before_request():
    """请求前的钩子"""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    """未确认用户视图"""
    if current_user.is_anonymous and current_user.confirmed:
        redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认邮件', 'auth/confirm', token=token, user=current_user)
    flash('一份新的确认邮件已发至您的邮箱,请及时进行账户确认!')
    return render_template(url_for('main.index'))


@auth.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('your password has been upgrade!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change-password.html', form=form)
