from flask import Flask
from sqlalchemy import text
import config
from exts import db
# 导入模型
from models import Usermodel,Attendancemodel,Leavetbmodel
# 导入蓝图
from blueprints.auth import auth_bp
from blueprints.leave import leave_bp
from blueprints.attendance import attendance_bp
from blueprints.admin import admin_bp
from flask_migrate import  Migrate
# 导入触发器函数
from sqlyj import create_all_triggers  

app = Flask(__name__)
# 绑定配置文件--数据库
app.config.from_object(config)
# 设置SECRET_KEY用于session管理
app.config['SECRET_KEY'] = 'your-secret-key'
db.init_app(app)

migrate = Migrate(app, db)

#  注册蓝图
app.register_blueprint(leave_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(admin_bp)

# 创建所有触发器
with app.app_context():
    create_all_triggers()




if __name__ == '__main__':
    app.run(debug=True)
