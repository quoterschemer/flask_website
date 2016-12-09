#encoding: utf-8
import os
import re
import json
import random
import urllib
import datetime

from .. import db
from . import main
from .forms import  PostForm
from ..decorators import permission_required, admin_required
from ..models import Permission,Post,Role,User
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.login import login_required, current_user
from flask import render_template, redirect, url_for,flash,request, make_response,abort,\
        current_app
from werkzeug import secure_filename
UPLOAD_FOLDER='/home/monkey/website/flask/app/static/upload/'
ALLOWED_EXTENSIONS = set(['txt','jpg','png','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['AUTOCAR_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                    'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                    % (query.statement, query.parameters, query.duration,
                        query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['AUTOCAR_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html',posts=posts,pagination=pagination)


@main.route('/post-article', methods=['GET', 'POST'])
@login_required
def post_article():
    if not current_user.can(Permission.WRITE_ARTICLES):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        #filter cover img
        coverFile = request.files['cover']
        if coverFile and allowed_file(coverFile.filename):
            filename = secure_filename(coverFile.filename)
            coverFile.save(os.path.join(UPLOAD_FOLDER, filename))
            cover = url_for('static',filename="upload/"+filename)
        else:
            body=form.editor1.data
            cover=re.findall(r"<img.+src=[\"|\']([^=]+)[\"|\'] *.*>",body)
            if len(cover) == 0 :
                abort(403)
            else:
                cover = cover[0]
        post = Post(title=form.title.data,
                abstract=form.abstract.data,
                cover=cover,
                body=form.editor1.data,
                author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    return render_template('post_article.html',form=form)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    post.viewed()
    return render_template('post.html',post=post)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.is_administrater():
                abort(403)

    form = PostForm()
    if form.validate_on_submit():
        coverFile = request.files['cover']
        if coverFile and allowed_file(coverFile.filename):
            filename = secure_filename(coverFile.filename)
            coverFile.save(os.path.join(UPLOAD_FOLDER,filename))
            cover = url_for('static', filename='upload/'+filename)
        else:
            body=form.editor1.data
            cover=re.findall(r"<img.+src=[\"|\']([^=]+)[\"|\'] *.*>",body)
            if len(cover) == 0 :
                abort(403)
            else:
                cover = cover[0]

        post.title = form.title.data
        post.abstract = form.abstract.data
        post.cover = cover
        post.body = form.editor1.data
        db.session.add(post)
        flash("文章已被更改")
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.abstract.data = post.abstract
    form.cover.data = post.cover
    form.editor1.data = post.body
    return render_template("edit_post.html", form=form)






def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/ckupload/', methods=['POST'])
def ckupload():
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join('/home/monkey/website/flask/app/static/', 'upload', rnd_name)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """

<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>

""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

