import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Usermodel, Attendancemodel, Leavetbmodel

# 测试触发器的函数
def test_triggers():
    with app.app_context():
        try:
            print("开始测试数据库触发器...")
            
            # 先确保管理员用户存在
            admin_employee = Usermodel.query.filter_by(job_id=9999).first()
            if not admin_employee:
                admin_employee = Usermodel(
                    job_id=9999,
                    name='管理员',
                    password='admin123',
                    type='管理员',
                    gender='男',
                    duty='系统管理员'
                )
                db.session.add(admin_employee)
                db.session.commit()
                print("创建管理员成功")
            else:
                print("管理员已存在")
            
            # 创建一个测试员工（如果不存在）
            test_employee = Usermodel.query.filter_by(job_id=1001).first()
            if not test_employee:
                test_employee = Usermodel(
                    job_id=1001,
                    name='测试员工',
                    password='123456',
                    type='工作人员',
                    gender='男',
                    duty='测试工程师'
                )
                db.session.add(test_employee)
                db.session.commit()
                print("创建测试员工成功")
            else:
                print("测试员工已存在")
            
            # 测试签到触发器
            # 先删除已有的测试签到记录
            Attendancemodel.query.filter_by(adjob_id=1001).delete()
            db.session.commit()
            
            # 创建新的签到记录
            checkin_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            attendance = Attendancemodel(
                adjob_id=1001,
                begin_date=checkin_time,
                begin_type='正常',
                leave_type='否'
            )
            db.session.add(attendance)
            db.session.commit()
            print("创建签到记录成功，测试签到触发器")
            
            # 测试请假触发器
            # 先删除已有的测试请假记录
            Leavetbmodel.query.filter_by(job_id=1001).delete()
            db.session.commit()
            
            # 创建新的请假记录
            vacation_date = datetime.now() + timedelta(days=1)
            leave = Leavetbmodel(
                job_id=1001,
                handler_id=9999,
                ltb_type='待审批',
                ltb_day=1,
                ltb_txt='测试请假',
                vacation_time=vacation_date,
                application_time=datetime.now()
            )
            db.session.add(leave)
            db.session.commit()
            print("创建请假记录成功，测试请假触发器")
            
            # 查询创建的记录，验证触发器是否生效
            new_attendance = Attendancemodel.query.filter_by(adjob_id=1001).first()
            new_leave = Leavetbmodel.query.filter_by(job_id=1001).first()
            
            print(f"验证结果：\n- 签到记录ID: {new_attendance.Ad_id}\n- 请假记录ID: {new_leave.ltb_id}")
            print("触发器测试完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"触发器测试失败：{str(e)}")
        finally:
            # 清理测试数据
            try:
                Attendancemodel.query.filter_by(adjob_id=1001).delete()
                Leavetbmodel.query.filter_by(job_id=1001).delete()
                # 保留管理员账户，不删除
                # Usermodel.query.filter_by(job_id=1001).delete()
                db.session.commit()
                print("清理测试数据成功")
            except Exception as e:
                print(f"清理测试数据失败：{str(e)}")

if __name__ == '__main__':
    test_triggers()