from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# SMTP服务器配置
app.config["MAIL_SERVER"] = "smtp.126.com"  # 电子邮件服务器的主机名或IP地址
app.config["MAIL_PORT"] = 25 # 电子邮件服务器的端口
app.config["MAIL_USE_TLS"] = True  # 启用传输层安全
# 注意这里启用的是TLS协议(transport layser security),而不是SSL协议所以用的是25号端口
app.config["MAIL_USERNAME"] = "ybw1999724@126.com"  # 你的邮箱用户名
app.config["MAIL_PASSWORD"] = "p0o9i8"  # 邮箱账户密码，这个密码是指的 授权码

mail = Mail(app)


@app.route("/")
def index():
    msg = Message("我是大标题", sender="ybw1999724@126.com", recipients=["18319260857@126.com"])
    # 这里sender是发信人，写上你发信人的名字，比如张三
    # recipients是收信人，用一个列表表示

    msg.body = "你好"
    msg.html = "<b>呵呵呵</b>"
    mail.send(msg)
    return "<h1>邮箱发送成功</h1>"


if __name__ == '__main__':
    app.run()
