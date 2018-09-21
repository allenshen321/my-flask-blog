from flask.ext.wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import Role, User
from flask.ext.pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('家庭住址')
    about_me = TextAreaField('关于我的描述')
    submit = SubmitField('确认修改')


class EditProfileAdminForm(EditProfileForm):
    email = StringField('注册邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp(r'^[A-Za-z][A-Za-z0-9_.]*$', 0, message='用户名必须以字母开头,必须是数字,字母,_和.')])
    confirmed = BooleanField('是否进行过邮件确认')
    role = SelectField('角色级别', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('家庭住址')
    about_me = TextAreaField('关于我的描述')
    submit = SubmitField('确认修改')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email \
                and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册过了!!!')

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被用了!!!')


class PostForm(FlaskForm):
    title = StringField('文章标题', validators=[DataRequired(), Length(1, 64)])
    # body = TextAreaField('文章内容', validators=[DataRequired()])
    body = PageDownField('文章内容:', validators=[DataRequired()])  # 支持markdown富文本
    submit = SubmitField('提交文章')


class EditPostForm(FlaskForm):
    title = StringField('文章标题:', validators=[DataRequired()])
    body = PageDownField('文章:')
    submit = SubmitField('确认修改')


class CommentForm(FlaskForm):
    body = StringField('请输入你的评论:', validators=[DataRequired()])
    submit = SubmitField('提交评论')
