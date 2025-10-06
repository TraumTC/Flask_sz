from flask import Blueprint

# 蓝图    （蓝图名称，蓝图导入上下文，url前缀）
auth_bp=Blueprint("auto",__name__,url_prefix="/")

@auth_bp.route('/')
def index():
    return "欢迎来到Flask实战项目！"