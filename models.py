from exts import db

class Usermodel(db.Model):
    # 表名
    __tablename__ = "Users"

    # 字段映射（与SQL表完全对应）
    job_id = db.Column(db.Integer, primary_key=True, comment="工号（登录用）")
    name = db.Column(db.String(50), nullable=False, comment="姓名")
    password = db.Column(db.String(50), nullable=False, comment="密码")
    gender = db.Column(db.String(2), comment="性别（男/女）")
    duty = db.Column(db.String(20), comment="职务")
    type = db.Column(db.String(8), comment="人员类型（工作人员/管理员）")

    # 关联关系：一个用户对应多条考勤记录
    attendances = db.relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    # 关联关系：一个用户对应多个请假申请（作为申请人）
    leave_applications = db.relationship("LeaveTb", foreign_keys="[LeaveTb.job_id]", back_populates="applicant")
    # 关联关系：一个用户对应多个请假审核（作为审核人）
    handled_leaves = db.relationship("LeaveTb", foreign_keys="[LeaveTb.handler_id]", back_populates="handler")

    # 约束定义（对应SQL中的CHECK）
    __table_args__ = (
        db.CheckConstraint("gender IN ('男', '女')", name="check_gender"),  # 性别只能是'男'或'女'
        db.CheckConstraint("type IN ('工作人员', '管理员')", name="check_user_type"),  # 人员类型限定
        {"comment": "用户信息表"}
    )


# 考勤表模型
class Attendancemodel(db.Model):
    # 表名
    __tablename__ = "Attendance"

    # 字段映射
    Ad_id = db.Column(db.Integer, autoincrement=True, primary_key=True, comment="序号")
    adjob_id = db.Column(db.Integer, db.ForeignKey("Users.job_id"), comment="关联工号")
    begin_date = db.Column(db.DateTime, comment="签到时间")
    begin_type = db.Column(db.String(20), comment="签到情况（正常、迟到、未签）")
    over_date = db.Column(db.DateTime, comment="签退时间")
    over_type = db.Column(db.String(20), comment="签退情况（正常、早退、未签）")

    # 关联关系：关联到用户表
    user = db.relationship("User", back_populates="attendances")

    __table_args__ = {"comment": "考勤记录表"}


# 请假情况表模型
class Leavetbmodel(db.Model):
    # 表名
    __tablename__ = "Leave_tb"
    # 字段映射
    ltb_id = db.Column(db.Integer, autoincrement=True, primary_key=True, comment="序号")
    job_id = db.Column(db.Integer, db.ForeignKey("Users.job_id"), nullable=False, comment="申请人工号")
    ltb_txt = db.Column(db.Text, comment="申请理由")
    handler_id = db.Column(db.Integer, db.ForeignKey("Users.job_id"), nullable=False, comment="审核员工号")
    ltb_type = db.Column(db.String(30), comment="申请状态（如：待审核、已批准、已拒绝）")
    application_time = db.Column(db.DateTime, comment="申请时间")
    audit_time = db.Column(db.DateTime, comment="审核时间")
    ltb_day = db.Column(db.Integer, comment="请假天数")
    vacation_time = db.Column(db.DateTime, comment="销假时间")
    overdue_type = db.Column(db.String(2), comment="逾期情况（是/否）")
    overdue_day = db.Column(db.Integer, comment="逾期天数")

    # 关联关系：关联到申请人（用户表）
    applicant = db.relationship("User", foreign_keys=[job_id], back_populates="leave_applications")
    # 关联关系：关联到审核人（用户表）
    handler = db.relationship("User", foreign_keys=[handler_id], back_populates="handled_leaves")

    # 约束定义（对应SQL中的CHECK）
    __table_args__ = (
        db.CheckConstraint("overdue_type IN ('是', '否')", name="check_overdue_type"),  # 逾期情况限定
        {"comment": "请假情况表"}
    )