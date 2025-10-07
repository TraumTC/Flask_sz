from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from exts import db
from models import Usermodel
import datetime

# 蓝图    （蓝图名称，蓝图导入上下文，url_prefix）
auth_bp = Blueprint("auth", __name__, url_prefix="/")

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # API登录接口
        if request.is_json:
            data = request.get_json()
            job_id = data.get('job_id')
            password = data.get('password')
        else:
            # 表单登录
            job_id = request.form.get('job_id')
            password = request.form.get('password')

        if not job_id or not password:
            if request.is_json:
                return jsonify({'code': 400, 'message': '工号和密码不能为空'})
            else:
                return render_template('login.html', error='工号和密码不能为空')

        user = Usermodel.query.filter_by(job_id=job_id, password=password).first()
        if not user:
            if request.is_json:
                return jsonify({'code': 401, 'message': '工号或密码错误'})
            else:
                return render_template('login.html', error='工号或密码错误')

        # 登录成功，设置session
        session['job_id'] = user.job_id
        session['name'] = user.name
        session['type'] = user.type

        if request.is_json:
            return jsonify({'code': 200, 'message': '登录成功', 'data': {
                'job_id': user.job_id,
                'name': user.name,
                'type': user.type
            }})
        else:
            # 根据用户类型跳转到不同页面
            if user.type == '管理员':
                return redirect(url_for('auth.admin_dashboard'))
            else:
                return redirect(url_for('auth.employee_dashboard'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # API注册接口
        if request.is_json:
            data = request.get_json()
            job_id = data.get('job_id')
            name = data.get('name')
            password = data.get('password')
            gender = data.get('gender')
            duty = data.get('duty')
        else:
            # 表单注册
            job_id = request.form.get('job_id')
            name = request.form.get('name')
            password = request.form.get('password')
            gender = request.form.get('gender')
            duty = request.form.get('duty')

        if not all([job_id, name, password, gender, duty]):
            if request.is_json:
                return jsonify({'code': 400, 'message': '所有字段不能为空'})
            else:
                return render_template('register.html', error='所有字段不能为空')

        # 检查工号是否已存在
        existing_user = Usermodel.query.filter_by(job_id=job_id).first()
        if existing_user:
            if request.is_json:
                return jsonify({'code': 400, 'message': '工号已存在'})
            else:
                return render_template('register.html', error='工号已存在')

        # 创建新用户，默认类型为工作人员
        new_user = Usermodel(
            job_id=job_id,
            name=name,
            password=password,
            gender=gender,
            duty=duty,
            type='工作人员'
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            if request.is_json:
                return jsonify({'code': 200, 'message': '注册成功'})
            else:
                return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'code': 500, 'message': f'注册失败：{str(e)}'})
            else:
                return render_template('register.html', error=f'注册失败：{str(e)}')

@auth_bp.route('/logout')
def logout():
    # 清除session
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/employee_dashboard')
def employee_dashboard():
    if 'job_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('employee_dashboard.html', name=session['name'])

@auth_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'job_id' not in session or session['type'] != '管理员':
        return redirect(url_for('auth.login'))
    return render_template('admin_dashboard.html', name=session['name'])