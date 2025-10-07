from flask import Blueprint, request, jsonify, session, render_template
from exts import db
from models import Usermodel
from blueprints.attendance import get_attendance_report, export_report

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route('/employees', methods=['GET'])
def get_employees():
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    # 构建查询
    query = Usermodel.query
    if search:
        query = query.filter(
            (Usermodel.job_id == int(search) if search.isdigit() else False) |
            Usermodel.name.like(f'%{search}%') |
            Usermodel.duty.like(f'%{search}%')
        )

    # 分页查询
    pagination = query.order_by(Usermodel.job_id).paginate(page=page, per_page=per_page, error_out=False)
    employees = pagination.items

    # 格式化返回数据
    result = []
    for employee in employees:
        result.append({
            'job_id': employee.job_id,
            'name': employee.name,
            'gender': employee.gender,
            'duty': employee.duty,
            'type': employee.type
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'employees': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })

@admin_bp.route('/employee/<int:job_id>', methods=['GET'])
def get_employee_detail(job_id):
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 查找员工
    employee = Usermodel.query.get(job_id)
    if not employee:
        return jsonify({'code': 404, 'message': '员工不存在'})

    # 格式化返回数据
    result = {
        'job_id': employee.job_id,
        'name': employee.name,
        'gender': employee.gender,
        'duty': employee.duty,
        'type': employee.type
    }

    return jsonify({'code': 200, 'message': '查询成功', 'data': result})

@admin_bp.route('/employee', methods=['POST'])
def add_employee():
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 获取请求数据
    if request.is_json:
        data = request.get_json()
        job_id = data.get('job_id')
        name = data.get('name')
        password = data.get('password')
        gender = data.get('gender')
        duty = data.get('duty')
        user_type = data.get('type', '工作人员')  # 默认是工作人员
    else:
        job_id = request.form.get('job_id')
        name = request.form.get('name')
        password = request.form.get('password')
        gender = request.form.get('gender')
        duty = request.form.get('duty')
        user_type = request.form.get('type', '工作人员')

    # 验证数据
    if not all([job_id, name, password, gender, duty]):
        return jsonify({'code': 400, 'message': '所有字段不能为空'})

    # 检查工号是否已存在
    existing_employee = Usermodel.query.filter_by(job_id=job_id).first()
    if existing_employee:
        return jsonify({'code': 400, 'message': '工号已存在'})

    # 创建新员工
    new_employee = Usermodel(
        job_id=job_id,
        name=name,
        password=password,
        gender=gender,
        duty=duty,
        type=user_type
    )

    try:
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({'code': 200, 'message': '员工添加成功', 'data': {
            'job_id': new_employee.job_id,
            'name': new_employee.name
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'员工添加失败：{str(e)}'})

@admin_bp.route('/employee/<int:job_id>', methods=['PUT'])
def update_employee(job_id):
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 查找员工
    employee = Usermodel.query.get(job_id)
    if not employee:
        return jsonify({'code': 404, 'message': '员工不存在'})

    # 获取请求数据
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')
        gender = data.get('gender')
        duty = data.get('duty')
        user_type = data.get('type')
    else:
        name = request.form.get('name')
        password = request.form.get('password')
        gender = request.form.get('gender')
        duty = request.form.get('duty')
        user_type = request.form.get('type')

    # 更新员工信息
    if name:
        employee.name = name
    if password:
        employee.password = password
    if gender:
        employee.gender = gender
    if duty:
        employee.duty = duty
    if user_type:
        employee.type = user_type

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '员工信息更新成功', 'data': {
            'job_id': employee.job_id,
            'name': employee.name
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'员工信息更新失败：{str(e)}'})

@admin_bp.route('/employee/<int:job_id>', methods=['DELETE'])
def delete_employee(job_id):
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 不能删除自己
    if job_id == session['job_id']:
        return jsonify({'code': 400, 'message': '不能删除自己'})

    # 查找员工
    employee = Usermodel.query.get(job_id)
    if not employee:
        return jsonify({'code': 404, 'message': '员工不存在'})

    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'code': 200, 'message': '员工删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'员工删除失败：{str(e)}'})