class Config(object):
    """项目共用的一些配置"""

    SECRET_KEY = "123456"


class DevelopmentConfig(Config):
    """开发环境"""
    DEBUG = True  # 打开测试

    # 数据库相关配置
    # 设置数据库的链接地址
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@localhost:3306/flask_test1?charset=utf8'
    # 关闭追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP服务器配置
    MAIL_SERVER = "smtp.126.com"  # 电子邮件服务器的主机名或IP地址
    MAIL_PORT = 25  # 电子邮件服务器的端口
    MAIL_USE_TLS = True  # 启用传输层安全
    # 注意这里启用的是TLS协议(transport layser security),而不是SSL协议所以用的是25号端口
    MAIL_USERNAME = "ybw1999724@126.com"  # 你的邮箱用户名
    MAIL_PASSWORD = "p0o9i8"  # 邮箱账户密码，这个密码是指的 授权码


class ProductionConfig(Config):
    """生产环境"""
    DEBUG = False  # 打开测试


APPCONFIG = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
