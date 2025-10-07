from flask import Blueprint, request, jsonify, session
from exts import db
from models import Leavetbmodel, Usermodel
import datetime

leave_bp = Blueprint("leave", __name__, url_prefix="/api")

@leave_bp.route('/leave', methods=['POST'])
def apply_leave():
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    job_id = session['job_id']
    # API请求处理
    if request.is_json:
        data = request.get_json()
        reason = data.get('reason')
        days = data.get('days')
    else:
        # 表单请求处理
        reason = request.form.get('reason')
        days = request.form.get('days')

    if not reason or not days:
        return jsonify({'code': 400, 'message': '请假理由和天数不能为空'})

    try:
        days = int(days)
        if days <= 0:
            return jsonify({'code': 400, 'message': '请假天数必须大于0'})
    except ValueError:
        return jsonify({'code': 400, 'message': '请假天数必须是数字'})

    # 查询管理员作为审核人（取第一个管理员）
    admin = Usermodel.query.filter_by(type='管理员').first()
    if not admin:
        return jsonify({'code': 500, 'message': '系统中没有管理员，请联系系统管理员'})

    # 创建请假申请
    new_leave = Leavetbmodel(
        job_id=job_id,
        ltb_txt=reason,
        handler_id=admin.job_id,
        ltb_day=days
    )

    try:
        db.session.add(new_leave)
        db.session.commit()
        # 更新考勤记录中的请假情况
        # 获取当前时间所在月份的第一天和最后一天
        now = datetime.datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end_of_month = start_of_month.replace(year=now.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=now.month + 1)
        
        # 更新该月的考勤记录
        from models import Attendancemodel
        attendance_records = Attendancemodel.query.filter(
            Attendancemodel.adjob_id == job_id,
            Attendancemodel.begin_date >= start_of_month,
            Attendancemodel.begin_date < end_of_month
        ).all()
        
        for record in attendance_records:
            record.leave_type = '是'
        
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '请假申请提交成功', 'data': {
            'leave_id': new_leave.ltb_id,
            'status': new_leave.ltb_type
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'请假申请失败：{str(e)}'})

@leave_bp.route('/leave/<int:leave_id>', methods=['PUT'])
def approve_leave(leave_id):
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    admin_id = session['job_id']

    # 查找请假申请
    leave = Leavetbmodel.query.get(leave_id)
    if not leave:
        return jsonify({'code': 404, 'message': '请假申请不存在'})

    # 检查是否是该请假申请的审核人
    if leave.handler_id != admin_id:
        return jsonify({'code': 403, 'message': '您不是该请假申请的审核人'})

    # 检查请假申请状态
    if leave.ltb_type in ['已批准', '已拒绝']:
        return jsonify({'code': 400, 'message': '该请假申请已经处理过了'})

    # 获取审批结果
    if request.is_json:
        data = request.get_json()
        status = data.get('status')
    else:
        status = request.form.get('status')

    if not status or status not in ['已批准', '已拒绝']:
        return jsonify({'code': 400, 'message': '审批结果必须是"已批准"或"已拒绝"'})

    # 更新请假申请状态
    leave.ltb_type = status

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '请假审批成功', 'data': {
            'leave_id': leave.ltb_id,
            'status': leave.ltb_type,
            'audit_time': leave.audit_time.strftime('%Y-%m-%d %H:%M:%S') if leave.audit_time else None
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'请假审批失败：{str(e)}'})

@leave_bp.route('/leave/list', methods=['GET'])
def get_leave_list():
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    job_id = session['job_id']
    user_type = session['type']

    # 构建查询条件
    if user_type == '管理员':
        # 管理员可以查看所有请假申请
        leaves = Leavetbmodel.query.order_by(Leavetbmodel.application_time.desc()).all()
    else:
        # 普通员工只能查看自己的请假申请
        leaves = Leavetbmodel.query.filter_by(job_id=job_id).order_by(Leavetbmodel.application_time.desc()).all()

    # 格式化返回数据
    result = []
    for leave in leaves:
        # 获取申请人信息
        applicant = Usermodel.query.get(leave.job_id)
        # 获取审核人信息
        handler = Usermodel.query.get(leave.handler_id)
        
        result.append({
            'leave_id': leave.ltb_id,
            'applicant_id': leave.job_id,
            'applicant_name': applicant.name if applicant else '',
            'reason': leave.ltb_txt,
            'days': leave.ltb_day,
            'handler_id': leave.handler_id,
            'handler_name': handler.name if handler else '',
            'status': leave.ltb_type,
            'application_time': leave.application_time.strftime('%Y-%m-%d %H:%M:%S') if leave.application_time else None,
            'audit_time': leave.audit_time.strftime('%Y-%m-%d %H:%M:%S') if leave.audit_time else None
        })

    return jsonify({'code': 200, 'message': '查询成功', 'data': result})

@leave_bp.route('/leave/<int:leave_id>', methods=['GET'])
def get_leave_detail(leave_id):
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    job_id = session['job_id']
    user_type = session['type']

    # 查找请假申请
    leave = Leavetbmodel.query.get(leave_id)
    if not leave:
        return jsonify({'code': 404, 'message': '请假申请不存在'})

    # 检查权限：只能查看自己的或自己审核的请假申请，或者管理员可以查看所有
    if user_type != '管理员' and leave.job_id != job_id and leave.handler_id != job_id:
        return jsonify({'code': 403, 'message': '没有权限查看该请假申请'})

    # 获取申请人信息
    applicant = Usermodel.query.get(leave.job_id)
    # 获取审核人信息
    handler = Usermodel.query.get(leave.handler_id)

    # 格式化返回数据
    result = {
        'leave_id': leave.ltb_id,
        'applicant_id': leave.job_id,
        'applicant_name': applicant.name if applicant else '',
        'reason': leave.ltb_txt,
        'days': leave.ltb_day,
        'handler_id': leave.handler_id,
        'handler_name': handler.name if handler else '',
        'status': leave.ltb_type,
        'application_time': leave.application_time.strftime('%Y-%m-%d %H:%M:%S') if leave.application_time else None,
        'audit_time': leave.audit_time.strftime('%Y-%m-%d %H:%M:%S') if leave.audit_time else None,
        'vacation_time': leave.vacation_time.strftime('%Y-%m-%d %H:%M:%S') if leave.vacation_time else None,
        'overdue_type': leave.overdue_type,
        'overdue_day': leave.overdue_day
    }

    return jsonify({'code': 200, 'message': '查询成功', 'data': result})

