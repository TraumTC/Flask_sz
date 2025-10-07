from sqlalchemy import text
from exts import db

def create_ad_begin_type():
    """创建签到触发器"""
    sql = """
    CREATE TRIGGER ad_begin_type
    BEFORE INSERT ON Attendance
    FOR EACH ROW
    BEGIN
        -- 当输入了签到时间时，判断签到情况
        IF NEW.begin_date IS NOT NULL THEN
            IF TIME(NEW.begin_date) > '08:30:00' THEN
                SET NEW.begin_type = '迟到';
            ELSE
                SET NEW.begin_type = '正常';
            END IF;
        END IF;
    END 
    """
    try:
        with db.engine.begin() as connection:
            connection.execute(text(sql))
        print("签到触发器创建成功")
        return True
    except Exception as e:
        print(f"签到触发器失败: {e}")
        return False


def create_ad_over_type():
    """创建签退触发器"""
    sql = """
    CREATE TRIGGER set_attendance_over_type
    BEFORE UPDATE ON Attendance
    FOR EACH ROW
    BEGIN
        -- 当输入签退时间时，判断签退情况
        IF NEW.over_date IS NOT NULL THEN
            IF TIME(NEW.over_date) > '17:30:00' THEN
                SET NEW.over_type = '正常';
            ELSE
                SET NEW.over_type = '早退';
            END IF;
        END IF;
    END 
    """
    try:
        with db.engine.begin() as connection:
            connection.execute(text(sql))
        print("签退触发器创建成功")
        return True
    except Exception as e:
        print(f"签退触发器失败: {e}")
        return False


def create_leave_defaults():
    """创建请假默认状态触发器"""
    sql = """
    CREATE TRIGGER set_leave_application_defaults
    BEFORE INSERT ON Leave_tb
    FOR EACH ROW
    BEGIN
        -- 设置默认申请状态为"待审核"
        SET NEW.ltb_type = '待审核';
        -- 设置申请时间为当前系统时间
        SET NEW.application_time = NOW();
    END
    """
    try:
        with db.engine.begin() as connection:
            connection.execute(text(sql))
        print("请假默认状态触发器创建成功")
        return True
    except Exception as e:
        print(f"请假默认状态触发器失败: {e}")
        return False


def create_leave_update():
    """创建请假默认状态触发器"""
    sql = """
    CREATE TRIGGER leave_update
    BEFORE UPDATE ON Leave_tb
    FOR EACH ROW
    BEGIN
        -- 当审核状态变为"已批准"或"已拒绝"时，设置审核时间为当前时间
        IF NEW.ltb_type IN ('已批准', '已拒绝') AND OLD.ltb_type != NEW.ltb_type THEN
            SET NEW.audit_time = NOW();
        END IF;
    END 
          """
    try:
        with db.engine.begin() as connection:
            connection.execute(text(sql))
        print("请假更新状态触发器创建成功")
        return True
    except Exception as e:
        print(f"请假更新状态触发器失败: {e}")
        return False

def create_leave_overdue():
    """创建销假状态触发器"""
    sql = """
    CREATE TRIGGER leave_overdue
    BEFORE UPDATE ON Leave_tb
    FOR EACH ROW
    BEGIN
        -- 当销假时间被设置或更新时进行计算
        IF NEW.vacation_time IS NOT NULL THEN
            -- 计算实际请假天数（销假时间 - 审核时间）
            SET @actual_days = DATEDIFF(NEW.vacation_time, OLD.audit_time);
            
            -- 判断是否逾期
            IF @actual_days > OLD.ltb_day THEN
                SET NEW.overdue_type = '是';
                SET NEW.overdue_day = @actual_days - OLD.ltb_day;
            ELSE
                SET NEW.overdue_type = '否';
                SET NEW.overdue_day = 0;
            END IF;
        END IF;
    END 
        """
    try:
        with db.engine.begin() as connection:
            connection.execute(text(sql))
        print("请假销假触发器创建成功")
        return True
    except Exception as e:
        print(f"请假销假触发器失败: {e}")
        return False





