#encoding: utf-8
from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField,TextField,FileField
from wtforms.validators import Required

class PostForm(Form):
    title = TextField('标题',validators=[Required()])
    abstract = TextAreaField('摘要')
    cover = FileField('封面图片')
    editor1 = TextAreaField('正文',validators=[Required()])
    submit =SubmitField('发表')
