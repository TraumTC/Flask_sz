from flask import Blueprint, request, jsonify, render_template, session
from exts import db
from models import Attendancemodel, Usermodel
import datetime
from sqlalchemy import func

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api")

@attendance_bp.route('/checkin', methods=['POST'])
def checkin():
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    job_id = session['job_id']
    today = datetime.date.today()
    now = datetime.datetime.now()

    # 检查今天是否已经签到
    existing_record = Attendancemodel.query.filter(
        Attendancemodel.adjob_id == job_id,
        func.date(Attendancemodel.begin_date) == today
    ).first()

    if existing_record:
        return jsonify({'code': 400, 'message': '今天已经签到过了'})

    # 创建新的签到记录
    new_record = Attendancemodel(
        adjob_id=job_id,
        begin_date=now,
        leave_type='否'  # 默认没有请假
    )

    try:
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'code': 200, 'message': '签到成功', 'data': {
            'checkin_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'签到失败：{str(e)}'})

@attendance_bp.route('/checkout', methods=['POST'])
def checkout():
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    job_id = session['job_id']
    today = datetime.date.today()
    now = datetime.datetime.now()

    # 查找今天的签到记录
    record = Attendancemodel.query.filter(
        Attendancemodel.adjob_id == job_id,
        func.date(Attendancemodel.begin_date) == today
    ).first()

    if not record:
        return jsonify({'code': 400, 'message': '请先签到'})

    if record.over_date:
        return jsonify({'code': 400, 'message': '今天已经签退过了'})

    # 更新签退时间
    record.over_date = now

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '签退成功', 'data': {
            'checkout_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'签退失败：{str(e)}'})

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    # 检查是否登录
    if 'job_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})

    # 获取查询参数
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')

    # 如果是管理员，可以查询所有员工；如果是普通员工，只能查询自己
    if session['type'] != '管理员' and (not employee_id or int(employee_id) != session['job_id']):
        employee_id = session['job_id']

    # 构建查询条件
    query = Attendancemodel.query
    if employee_id:
        query = query.filter(Attendancemodel.adjob_id == employee_id)
    if month:
        # 解析月份格式 YYYY-MM
        try:
            year, month_num = map(int, month.split('-'))
            start_date = datetime.date(year, month_num, 1)
            # 计算下个月的第一天
            if month_num == 12:
                end_date = datetime.date(year + 1, 1, 1)
            else:
                end_date = datetime.date(year, month_num + 1, 1)
            # 添加日期范围过滤
            query = query.filter(
                Attendancemodel.begin_date >= start_date,
                Attendancemodel.begin_date < end_date
            )
        except ValueError:
            return jsonify({'code': 400, 'message': '月份格式不正确，请使用YYYY-MM格式'})

    # 执行查询并排序
    records = query.order_by(Attendancemodel.begin_date.desc()).all()

    # 格式化返回数据
    result = []
    for record in records:
        result.append({
            'id': record.Ad_id,
            'date': record.begin_date.strftime('%Y-%m-%d') if record.begin_date else None,
            'checkin_time': record.begin_date.strftime('%H:%M:%S') if record.begin_date else None,
            'checkin_type': record.begin_type,
            'checkout_time': record.over_date.strftime('%H:%M:%S') if record.over_date else None,
            'checkout_type': record.over_type,
            'leave_type': record.leave_type
        })

    return jsonify({'code': 200, 'message': '查询成功', 'data': result})

@attendance_bp.route('/attendance_report', methods=['GET'])
def get_attendance_report():
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 获取月份参数
    month = request.args.get('month')
    if not month:
        # 默认查询当月
        now = datetime.datetime.now()
        month = f"{now.year}-{now.month:02d}"

    try:
        year, month_num = map(int, month.split('-'))
        start_date = datetime.date(year, month_num, 1)
        # 计算下个月的第一天
        if month_num == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month_num + 1, 1)
    except ValueError:
        return jsonify({'code': 400, 'message': '月份格式不正确，请使用YYYY-MM格式'})

    # 查询该月的所有考勤记录并按员工分组
    # 使用SQLAlchemy的核心表达式来执行复杂查询
    from sqlalchemy import text
    sql = """
    SELECT u.job_id, u.name, 
           COUNT(*) as total_days,
           SUM(CASE WHEN a.begin_type = '正常' AND a.over_type = '正常' THEN 1 ELSE 0 END) as normal_days,
           SUM(CASE WHEN a.begin_type = '迟到' THEN 1 ELSE 0 END) as late_days,
           SUM(CASE WHEN a.over_type = '早退' THEN 1 ELSE 0 END) as early_leave_days,
           SUM(CASE WHEN a.begin_date IS NULL OR a.over_date IS NULL THEN 1 ELSE 0 END) as absent_days,
           SUM(CASE WHEN a.leave_type = '是' THEN 1 ELSE 0 END) as leave_days
    FROM Users u
    LEFT JOIN Attendance a ON u.job_id = a.adjob_id 
        AND a.begin_date >= :start_date 
        AND a.begin_date < :end_date
    GROUP BY u.job_id, u.name
    ORDER BY u.job_id
    """

    try:
        with db.engine.connect() as connection:
            result = connection.execute(text(sql), {
                'start_date': start_date,
                'end_date': end_date
            })
            report_data = []
            for row in result:
                report_data.append({
                    'job_id': row.job_id,
                    'name': row.name,
                    'total_days': row.total_days,
                    'normal_days': row.normal_days,
                    'late_days': row.late_days,
                    'early_leave_days': row.early_leave_days,
                    'absent_days': row.absent_days,
                    'leave_days': row.leave_days
                })
        return jsonify({'code': 200, 'message': '查询成功', 'data': report_data, 'month': month})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败：{str(e)}'})

@attendance_bp.route('/export_report', methods=['GET'])
def export_report():
    # 检查是否是管理员
    if 'job_id' not in session or session['type'] != '管理员':
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'})

    # 获取月份参数
    month = request.args.get('month')
    if not month:
        # 默认查询当月
        now = datetime.datetime.now()
        month = f"{now.year}-{now.month:02d}"

    try:
        year, month_num = map(int, month.split('-'))
        start_date = datetime.date(year, month_num, 1)
        # 计算下个月的第一天
        if month_num == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month_num + 1, 1)
    except ValueError:
        return jsonify({'code': 400, 'message': '月份格式不正确，请使用YYYY-MM格式'})

    # 查询该月的所有考勤记录
    sql = """
    SELECT u.job_id, u.name, a.begin_date, a.begin_type, a.over_date, a.over_type, a.leave_type
    FROM Attendance a
    JOIN Users u ON a.adjob_id = u.job_id
    WHERE a.begin_date >= :start_date AND a.begin_date < :end_date
    ORDER BY u.job_id, a.begin_date
    """

    try:
        import csv
        from io import StringIO
        from flask import make_response

        with db.engine.connect() as connection:
            result = connection.execute(text(sql), {
                'start_date': start_date,
                'end_date': end_date
            })

            # 创建CSV文件
            csv_output = StringIO()
            csv_writer = csv.writer(csv_output)
            # 写入表头
            csv_writer.writerow(['工号', '姓名', '日期', '签到时间', '签到情况', '签退时间', '签退情况', '请假情况'])
            # 写入数据
            for row in result:
                csv_writer.writerow([
                    row.job_id,
                    row.name,
                    row.begin_date.strftime('%Y-%m-%d') if row.begin_date else '',
                    row.begin_date.strftime('%H:%M:%S') if row.begin_date else '',
                    row.begin_type or '',
                    row.over_date.strftime('%H:%M:%S') if row.over_date else '',
                    row.over_type or '',
                    row.leave_type or ''
                ])

        # 创建响应
        response = make_response(csv_output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename="attendance_report_{month}.csv"'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导出失败：{str(e)}'})