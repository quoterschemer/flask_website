#encoding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64),
        Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('保持登陆')
    submit = SubmitField('登陆')

class RegistrationForm(Form):
    LANGUAGES=['utf-8','zh']
    email = StringField("邮箱", validators=[Required(), Length(1,64),
        Email()])
    username = StringField('昵称',validators=[Required(), Length(1,64)])
    password = PasswordField('密码',validators=[Required(), EqualTo('password2',message='not same')])
    password2= PasswordField('确认密码',validators=[Required()])
    submit   = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码',validators=[
        Required(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('更新密码')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64), Email()])
    submit = SubmitField('重置密码')

class PasswordResetForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64),Email()])
    password = PasswordField('新密码', validators=[Required(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('该邮箱未注册')

class ChangeEmailForm(Form):
    email = StringField('新邮箱',validators=[Required(), Length(1,64), Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('更新邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


