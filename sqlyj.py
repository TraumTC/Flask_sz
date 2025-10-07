from sqlalchemy import text
from exts import db
import re

def create_ad_begin_type():
    """创建签到触发器"""
    trigger_name = "ad_begin_type"
    
    # 首先检查触发器是否存在
    try:
        with db.engine.begin() as connection:
            check_sql = text(f"SHOW TRIGGERS LIKE '{trigger_name}'")
            result = connection.execute(check_sql).fetchall()
            if result:
                print(f"签到触发器 '{trigger_name}' 已存在，跳过创建")
                return True
    except Exception as e:
        print(f"检查签到触发器是否存在时出错: {e}")
        # 继续尝试创建，因为在某些MySQL版本中，SHOW TRIGGERS可能有不同的行为
    
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
        # 检查错误信息是否包含"Trigger already exists"
        if re.search(r'Trigger already exists', str(e)):
            print(f"签到触发器 '{trigger_name}' 已存在，跳过创建")
            return True
        print(f"签到触发器失败: {e}")
        return False


def create_ad_over_type():
    """创建签退触发器"""
    trigger_name = "set_attendance_over_type"
    
    # 首先检查触发器是否存在
    try:
        with db.engine.begin() as connection:
            check_sql = text(f"SHOW TRIGGERS LIKE '{trigger_name}'")
            result = connection.execute(check_sql).fetchall()
            if result:
                print(f"签退触发器 '{trigger_name}' 已存在，跳过创建")
                return True
    except Exception as e:
        print(f"检查签退触发器是否存在时出错: {e}")
        # 继续尝试创建，因为在某些MySQL版本中，SHOW TRIGGERS可能有不同的行为
    
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
        # 检查错误信息是否包含"Trigger already exists"
        if re.search(r'Trigger already exists', str(e)):
            print(f"签退触发器 '{trigger_name}' 已存在，跳过创建")
            return True
        print(f"签退触发器失败: {e}")
        return False


def create_leave_defaults():
    """创建请假默认状态触发器"""
    trigger_name = "set_leave_application_defaults"
    
    # 首先检查触发器是否存在
    try:
        with db.engine.begin() as connection:
            check_sql = text(f"SHOW TRIGGERS LIKE '{trigger_name}'")
            result = connection.execute(check_sql).fetchall()
            if result:
                print(f"请假默认状态触发器 '{trigger_name}' 已存在，跳过创建")
                return True
    except Exception as e:
        print(f"检查请假默认状态触发器是否存在时出错: {e}")
        # 继续尝试创建，因为在某些MySQL版本中，SHOW TRIGGERS可能有不同的行为
    
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
        # 检查错误信息是否包含"Trigger already exists"
        if re.search(r'Trigger already exists', str(e)):
            print(f"请假默认状态触发器 '{trigger_name}' 已存在，跳过创建")
            return True
        print(f"请假默认状态触发器失败: {e}")
        return False


def create_leave_update():
    """创建请假更新状态触发器"""
    trigger_name = "leave_update"
    
    # 首先检查触发器是否存在
    try:
        with db.engine.begin() as connection:
            check_sql = text(f"SHOW TRIGGERS LIKE '{trigger_name}'")
            result = connection.execute(check_sql).fetchall()
            if result:
                print(f"请假更新状态触发器 '{trigger_name}' 已存在，跳过创建")
                return True
    except Exception as e:
        print(f"检查请假更新状态触发器是否存在时出错: {e}")
        # 继续尝试创建，因为在某些MySQL版本中，SHOW TRIGGERS可能有不同的行为
    
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
        # 检查错误信息是否包含"Trigger already exists"
        if re.search(r'Trigger already exists', str(e)):
            print(f"请假更新状态触发器 '{trigger_name}' 已存在，跳过创建")
            return True
        print(f"请假更新状态触发器失败: {e}")
        return False

def create_leave_overdue():
    """创建销假状态触发器"""
    trigger_name = "leave_overdue"
    
    # 首先检查触发器是否存在
    try:
        with db.engine.begin() as connection:
            check_sql = text(f"SHOW TRIGGERS LIKE '{trigger_name}'")
            result = connection.execute(check_sql).fetchall()
            if result:
                print(f"请假销假触发器 '{trigger_name}' 已存在，跳过创建")
                return True
    except Exception as e:
        print(f"检查请假销假触发器是否存在时出错: {e}")
        # 继续尝试创建，因为在某些MySQL版本中，SHOW TRIGGERS可能有不同的行为
    
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
        # 检查错误信息是否包含"Trigger already exists"
        if re.search(r'Trigger already exists', str(e)):
            print(f"请假销假触发器 '{trigger_name}' 已存在，跳过创建")
            return True
        print(f"请假销假触发器失败: {e}")
        return False


def create_all_triggers():
    """创建所有触发器的主函数"""
    print("开始创建所有触发器...")
    
    # 触发器函数列表
    trigger_functions = [
        create_ad_begin_type,      # 签到触发器
        create_ad_over_type,       # 签退触发器  
        create_leave_defaults,     # 请假默认状态触发器
        create_leave_update,       # 请假更新状态触发器
        create_leave_overdue       # 销假状态触发器
    ]
    
    success_count = 0
    total_count = len(trigger_functions)
    
    for func in trigger_functions:
        try:
            if func():
                success_count += 1
        except Exception as e:
            print(f"执行触发器函数 {func.__name__} 时发生错误: {e}")
    
    print(f"触发器创建完成: {success_count}/{total_count} 个触发器创建成功")
    
    if success_count == total_count:
        print("所有触发器创建成功！")
        return True
    else:
        print(f"有 {total_count - success_count} 个触发器创建失败")
        return False





