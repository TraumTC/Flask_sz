from flask import Flask
from sqlalchemy import text
import config
from exts import db
# 导入模型
from models import Usermodel,Attendancemodel,Leavetbmodel
from blueprints.auth import auth_bp
from blueprints.leave import leave_bp
from sqlyj import execute_query
from flask_migrate import  Migrate  

app = Flask(__name__)
# 绑定配置文件--数据库
app.config.from_object(config)
db.init_app(app)

migrate = Migrate(app, db)

#  注册蓝图
app.register_blueprint(leave_bp)
app.register_blueprint(auth_bp)





with app.app_context():
    # SQLAIchemy 1.4+ 所有原始SQL语句 需要通过TEXT（）函数转换为可执行语句
    rows = execute_query("SELECT * FROM users")
    if not rows:
        print("No users found in table 'users'.")
    else:
        print(rows[0][0])



if __name__ == '__main__':
    app.run(debug=True)
