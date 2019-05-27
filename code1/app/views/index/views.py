# 从数据库查询数据 并且传给模板
import hashlib
import os
import traceback
import uuid
import flask
from flask import render_template, url_for, redirect, request, make_response, session, g, current_app
from flask_mail import Message
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from app import db, mail
# from app.models import User
from app.models.models import User
from app.utils.captcha.captcha import captcha
from app.utils.commons.commons import login_user_data
from . import index_blu


# LOGIN_FLAG = False  # 标记是否登录  默认没有登录


@index_blu.route('/profile_v7')
@login_user_data
def profile7():
    print(current_app.url_map)
    print(current_app.config["SECRET_KEY"])

    # 从g里面 获取到用户信息 在login_data 装饰器里已经提前查询好了
    user =g.user
    if user:

        return render_template('index/profile.html', user_name=user.user_name, short_description=user.short_description
                               , head_img=user.head_img)
    else:
        return '去<a href="http://127.0.0.1:5000/index/login.html">登录</a>'


@index_blu.route('/index.html')
def index():
    return 'index------'


@index_blu.route('/login.html')
def login():
    """显示登录页面"""
    return render_template('index/login.html')


@index_blu.route('/login', methods=['POST', 'GET'])
def login_vf():
    """处理登录验证的逻辑"""
    # 1获取get请求传来的用户名和密码
    # 请求对象request  是一个上下文对象 只能用于视图里
    # request.args 获取get请求传来的参数  得到的是一个字典 可以使用字典的语法 获取里面 的内容
    print('request.args----', request.args)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # request.form 获取post请求传来的参数 得到的是一个字典 可以使用字典的语法 获取里面 的内容
    print('request.form----', request.form)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # 获取用户名和密码
    username = request.form.get('username')
    password = request.form.get('password')
    print('username==', username)
    print('password==', password)
    # 2 根据用户名和密码去数据库查询 如果能查到 登录成功 如果不能 就提示登录失败

    # DBSession = sessionmaker(bind=engine)
    # sqlsession = DBSession()  # 获取会话对象

    global LOGIN_FLAG
    try:
        user = db.session.query(User).filter(and_(User.user_name == username, User.password == password)).one()
    except:
        # 出现异常 没有查询到用户 登录失败
        # make_response可以返回一个response对象 这样用response对象 就可以去设置cookie
        response = make_response('登录失败了 username = %s password = %s' % (username, password))
        # LOGIN_FLAG = False

        # response.set_cookie('login_flag', 'fail')
        session['login_flag'] = 'fail'
        # 自定义抛出异常
        # abort(500)
    else:
        # LOGIN_FLAG = True
        # 登录成功  redirect返回的是一个response对象 可以设置cookie
        response = redirect(url_for('index.profile7'))

        # response.set_cookie('login_flag', 'success')
        session['login_flag'] = 'success'
        # 把user_id也存进来2
        session['user_id'] = user.user_id

    finally:
        db.session.close()

    return response


@index_blu.route('/logout')
def logout():
    """退出登录"""
    # 获取response响应对象
    response = redirect(url_for("index.login"))
    # 把cookie登录相关的信息清除
    # response.delete_cookie('login_flag')
    # 清除session数据
    session.clear()

    return response


@index_blu.route("/register", methods=['GET', 'POST'])
def register():
    """显示注册页面 """
    # 判断请求方式
    if request.method == "POST":
        # print(request.form)
        # 提取 数据

        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        # 图片验证码
        captcha = request.form.get("captcha")

        # 只要有1个需要的数据，没有，那么就返回数据有误
        if not (email and username and password and captcha):
            # 返回对应的数据
            ret = {
                "status": 2,
                "msg": "输入数据有误，请重新输入"
            }
            return flask.jsonify(ret)

        # session里取出验证码
        session_captcha = session.get('captcha')
        # 判断验证码是否正确 转为小写判断 可以让用户忽略大小写输入
        if session_captcha.lower() != captcha.lower():
            # 返回对应的数据
            ret = {
                "status": 3,
                "msg": "验证码错误"
            }
            return flask.jsonify(ret)

        # 业务处理：注册用户
        # 判断是否注册过
        # 1. 业务处理
        # db_session = sessionmaker(bind=engine)()  # 生成会话对象
        # 去数据库查询 获取结果的第一条数据
        user_ret = db.session.query(User).filter(or_(User.email == email, User.user_name == username)).first()
        if user_ret:
            # 2. 如果邮箱或者用户名已经存在，则不允许使用
            # 3. 返回对应的数据
            ret = {
                "status": 1,
                "msg": "邮箱或用户名已存在，请修改"
            }
        else:
            # uuid随机生成一个激活码 uuid1返回的是uuid对象 需要强转成字符串
            active_key = str(uuid.uuid1())
            # 把激活码里的横杆替换成空
            active_key = active_key.replace("-", "")

            active_addr = request.host_url + "index/active?id={}&activekey={}".format(username, active_key)

            msg = Message("我是大标题", sender="ybw1999724@126.com", recipients=[email])
            # 这里sender是发信人，写上你发信人的名字，比如张三
            # recipients是收信人，用一个列表表示

            msg.body = "激活邮箱"
            msg.html = """<a href='{}'>点击激活</a>,如果有什么问题请联系...""".format(active_addr)
            # 发送
            mail.send(msg)

            # 3. 未注册，那么则进行注册 注意别忘了激活码
            new_user = User(email=email, user_id=username, password=password, user_name=username, activekey=active_key)
            db.session.add(new_user)
            db.session.commit()

            # 3. 返回对应的数据
            ret = {
                "status": 0,
                "msg": "注册成功"

            }
        db.session.close()
        return flask.jsonify(ret)
    elif request.method == "GET":
        # 如果是get请求  就是请求页面
        return render_template("index/register.html")


@index_blu.route("/captcha")
def generate_captcha():
    # 1. 获取到当前的图片编号id
    captcah_id = request.args.get('id')

    print(type(captcah_id), captcah_id)

    # 2. 生成验证码
    # 返回保存的图片名字  验证码值  图片二进制内容
    name, text, image = captcha.generate_captcha()

    # print("注册时的验证码为：", name, text, image)  # 图片名字  验证码值  图片二进制内容

    # 3. 将生成的图片验证码值作为value，存储到session中
    session["captcha"] = text

    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@ index_blu.route("/active")
def active():
    """激活功能"""
    # 获取用户id
    user_id = request.args.get("user_id")
    # 获取激活码
    activekey = request.args.get("activekey")
    print(activekey)
    print(111111111)
    try:
        # 去数据库查询
        user = db.session.query(User).filter(and_(User.user_id == user_id, User.activekey==activekey)).one()
    except Exception as e:
        print(e)
        traceback.print_exc()
        response_str = "激活失败，请从新注册"
    else:
        print(2222222222222)
        # 修改状态为1
        user.status = True
        # 提交
        db.session.commit()
        response_str = """激活成功<a herf='{}'>登录</a>""".format(url_for(".login"))

    return response_str


# @index_blu.route("/deit", methods=["GET", "POST"])
# @login_user_data
# def edit():
#     """编辑页面的显示 和数据的更新"""
#
#     # 获取当前用户对象
#     current_user = g.user
#
#     # 判断用户是否存在
#     if not current_user:
#         return redirect(url_for(".login"))
#
#     # 如果是get就是显示页面
#     if request.method == "GET":
#         return render_template("index/edit.html", user=g.user)
#     elif request.method == "POST":
#         # post就是保存更新数据
#         # 提取数据
#         # user_id = request.form.get("user_id")
#         username = request.form.get("username")
#         password = request.form.get("password")
#         email = request.form.get("email")
#         # image = request.from.get("image")
#         content = request.form.get("content")
#
#         # 当前应用路径
#         print(current_app.root_path)
#
#         # 获取头像
#         f = request.files.get("image")
#
#         if f:
#             # basepath = os.path.dirname(__file__)  # 当前文件所在路径
#             # 注意：没有文件夹一定要先创建，不然会提示没有路径
#
#             # 获取文件的后缀名
#             image_tyep = f.filename[f.filename.rfind(""):]
#
#             # 根据图片的二进制数据获取md5加密的一个字符串最为保存的名字
#             name_hash = hashlib.md5()
#             name_hash.update(f.filename.encode("utf-8"))
#             image_file_name = name_hash.hexdigest()
#
#             # 图片保存的名字 = md5加密一个字符串 + 原后缀
#             image_file = image_file_name + image_tyep
#             # 图片在服务器里的路径 注意提前创健好/static/upload/images文件夹
#             image_path = os.path.join("/static/upload/images", image_file)
#
#             # 图片的绝对路径
#             upload_path = os.path.join(current_app.root_path, "static/upload/images", image_file)
#             print(upload_path)
#             # 保存图片路径到数据库
#             current_user.head_img = image_path
#
#         # 修改用户信息 为新的信息
#         current_user.useer_name = username
#         current_user.password = password
#         current_user.email = email
#         current_user.short_description = content
#
#         # 提交数据
#         db.session.commit()
#
#         # 重新刷新编辑页面 显示新的信息
#         return redirect(url_for(".edit"))
