from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import current_user, login_required
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, EditPostForm, CommentForm
from .. import db
from ..decorators import admin_required, permission_required
from ..models import User, Post, Permission, Follows, Comment


@main.route('/', methods=['GET', 'POST'])
def index():
    """首页"""
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.body = form.body.data
        post.author = current_user._get_current_object()
        db.session.add(post)
        db.session.commit()
        flash('文章已保存')
        return redirect(url_for('.index'))
    # 添加分页功能
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASK_POSTS_PER_PAGE_COUNT'], error_out=True)
    posts = pagination.items
    return render_template(
        'index.html',
        form=form,
        posts=posts,
        current_time=datetime.utcnow(),
        pagination=pagination
    )


@main.route('/user/<username>')
def user(username):
    """用户信息"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).filter_by(author_id=user.id).paginate(page, per_page=current_app.config['FLASK_POSTS_PER_PAGE_COUNT'], error_out=True)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/follow/<username>')
@login_required
def follow(username):
    """
    关注路由
    :param username: 要关注的对象
    :return:
    """
    u = User.query.filter_by(username=username).first()
    if not u:
        flash('无效的username')
        return redirect(url_for('main.index'))
    current_user.follow(u)
    flash('已关注%s' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取消关注
    :param username: 取关对象
    :return:
    """
    u = User.query.filter_by(username=username).first()
    current_user.unfollow(u)
    flash('已经取消关注%s' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    """关注人列表路由"""
    u = User.query.filter_by(username=username).first()
    if not u:
        flash('请求的用户名无效')
        return redirect(url_for('main.user', username=username))
    page = request.args.get('page', 1, type=int)
    pagination = u.followers.paginate(page,
                                      per_page=current_app.config['FLASK_FOLLOW_PER_PAGE_COUNT'],
                                      error_out=True)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', pagination=pagination, user=u,
                           follows=follows, title='Followers of', endpoint='main.followers')


@main.route('/followed/<username>')
def followed(username):
    """关注我的人的列表"""
    u = User.query.filter_by(username=username).first()
    if not u:
        flash('输入的用户名无效!!!')
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = u.followed.paginate(page,
                                     per_page=current_app.config['FLASK_FOLLOW_PER_PAGE_COUNT'],
                                     error_out=True)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followed.html', pagination=pagination, user=u,
                           title='Followed of', follows=follows,
                           endpoint='main.followed')


@main.route('/editprofile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """修改个人资料"""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('用户资料已修改!')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit-profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    """管理员修改个人资料"""
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role_id = form.role.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('用户信息已经更新!')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit-profile.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    """显示文章视图"""
    comment_form = CommentForm()
    post = Post.query.get_or_404(id)
    if comment_form.validate_on_submit():
        if current_user.is_anonymous:
            abort(403)
        comment = Comment()
        comment.body = comment_form.body.data
        comment.author = current_user._get_current_object()
        comment.post = post
        db.session.add(comment)
        db.session.commit()
        flash('评论已提交!')
        return redirect(url_for('main.post', id=id, page=-1))  # page=-1 是为了显示最后一页的评论
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = post.comments.count() / current_app.config['FLASK_COMMENT_PER_PAGE_COUNT'] + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,
                                                                           per_page=current_app.config['FLASK_COMMENT_PER_PAGE_COUNT'],
                                                                           error_out=True)
    comments = pagination.items
    return render_template('post.html', posts=[post], user=post.author, pagination=pagination, comments=comments, form=comment_form, id=post.id)


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """修改文章"""
    # post = Post.query.filter_by(id=id).first()
    post = Post.query.get_or_404(id)
    form = EditPostForm()
    if form.validate_on_submit():
        if current_user.role_id == post.author.role.id or current_user.can(permissions=Permission.ADMINISTER):
            post.title = form.title.data
            post.body = form.body.data
            db.session.add(post)
            db.session.commit()
            flash('文章已经更新!')
            return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit-post.html', post=post, form=form)


@main.route('/show_followed/<username>')
def show_followed(username):
    res = make_response(redirect(url_for('main.user', username=username)))
    res.set_cookie('show_which', '2')
    return res


@main.route('/show_followers/<username>')
def show_followers(username):
    res = make_response(redirect(url_for('main.user', username=username)))
    res.set_cookie('show_which', '3')
    return res


@main.route('/moderate')
@login_required
@permission_required(permissions=Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENT_PER_PAGE_COUNT'], error_out=True)
    comments = pagination.items
    return render_template('moderate.html', pagination=pagination, comments=comments, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(permissions=Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    db.session.commit()
    flash('评论状态已改变!!!')
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('main.moderate', page=page))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(permissions=Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.add(comment)
    db.session.commit()
    flash('评论状态已改变')
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('main.moderate', page=page))
