import re
str='''<img src="/static/upload/hello.jpg" class="img-respon">
<p>hello world</p>
<img src="/static/upload/helloworld.jpg" class="img-respon">'''
print re.findall(r"<img.+src=[\"|\'](.+)[\"|\'] .*>",str)[0]
