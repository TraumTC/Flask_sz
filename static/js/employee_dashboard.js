// 员工主页JavaScript

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', function() {
    // 绑定签到按钮事件
    document.getElementById('checkinBtn').addEventListener('click', handleCheckin);
    
    // 绑定签退按钮事件
    document.getElementById('checkoutBtn').addEventListener('click', handleCheckout);
    
    // 绑定请假表单提交事件
    document.getElementById('leaveForm').addEventListener('submit', function(e) {
        e.preventDefault();
        handleLeaveApplication();
    });
    
    // 绑定考勤查询按钮事件
    document.getElementById('queryBtn').addEventListener('click', handleAttendanceQuery);
    
    // 初始化页面时加载当前月份的考勤数据
    const today = new Date();
    const currentMonth = today.toISOString().slice(0, 7);
    document.getElementById('queryMonth').value = currentMonth;
    
    // 加载考勤数据
    handleAttendanceQuery();
    
    // 加载请假记录
    loadLeaveRecords();
});

// 签到处理函数
function handleCheckin() {
    fetch('/api/checkin', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('签到请求失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('attendanceResult', data.message, data.code === 200);
        // 如果签到成功，更新考勤数据
        if (data.code === 200) {
            handleAttendanceQuery();
        }
    })
    .catch(error => {
        showResult('attendanceResult', '签到失败：' + error.message, false);
    });
}

// 签退处理函数
function handleCheckout() {
    fetch('/api/checkout', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('签退请求失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('attendanceResult', data.message, data.code === 200);
        // 如果签退成功，更新考勤数据
        if (data.code === 200) {
            handleAttendanceQuery();
        }
    })
    .catch(error => {
        showResult('attendanceResult', '签退失败：' + error.message, false);
    });
}

// 请假申请处理函数
function handleLeaveApplication() {
    const reason = document.getElementById('leaveReason').value;
    const days = document.getElementById('leaveDays').value;
    
    if (!reason || !days) {
        showResult('leaveResult', '请假理由和天数不能为空', false);
        return;
    }
    
    if (parseInt(days) <= 0) {
        showResult('leaveResult', '请假天数必须大于0', false);
        return;
    }
    
    const formData = new FormData();
    formData.append('reason', reason);
    formData.append('days', days);
    
    fetch('/api/leave', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('请假申请请求失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('leaveResult', data.message, data.code === 200);
        // 如果请假申请成功，清空表单并更新请假记录
        if (data.code === 200) {
            document.getElementById('leaveForm').reset();
            loadLeaveRecords();
            handleAttendanceQuery();
        }
    })
    .catch(error => {
        showResult('leaveResult', '请假申请失败：' + error.message, false);
    });
}

// 考勤查询处理函数
function handleAttendanceQuery() {
    const month = document.getElementById('queryMonth').value;
    
    if (!month) {
        showResult('attendanceResult', '请选择查询月份', false);
        return;
    }
    
    fetch(`/api/attendance?month=${month}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('考勤查询请求失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderAttendanceTable(data.data);
        } else {
            showResult('attendanceResult', data.message, false);
        }
    })
    .catch(error => {
        showResult('attendanceResult', '考勤查询失败：' + error.message, false);
    });
}

// 加载请假记录
function loadLeaveRecords() {
    fetch('/api/leave/list')
    .then(response => {
        if (!response.ok) {
            throw new Error('请假记录请求失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderLeaveTable(data.data);
        }
    })
    .catch(error => {
        console.error('加载请假记录失败：', error);
    });
}

// 渲染考勤表格
function renderAttendanceTable(data) {
    const tableBody = document.getElementById('attendanceTableBody');
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6" style="text-align: center;">暂无考勤数据</td>';
        tableBody.appendChild(emptyRow);
        return;
    }
    
    data.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.date || '-'}</td>
            <td>${record.checkin_time || '-'}</td>
            <td>${record.checkin_type || '-'}</td>
            <td>${record.checkout_time || '-'}</td>
            <td>${record.checkout_type || '-'}</td>
            <td>${record.leave_type || '-'}</td>
        `;
        tableBody.appendChild(row);
    });
}

// 渲染请假表格
function renderLeaveTable(data) {
    const tableBody = document.getElementById('leaveTableBody');
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="5" style="text-align: center;">暂无请假记录</td>';
        tableBody.appendChild(emptyRow);
        return;
    }
    
    data.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.application_time || '-'}</td>
            <td>${record.reason || '-'}</td>
            <td>${record.days || '-'}</td>
            <td>${getStatusColor(record.status || '-')}</td>
            <td>${record.audit_time || '-'}</td>
        `;
        tableBody.appendChild(row);
    });
}

// 根据状态返回带颜色的HTML
function getStatusColor(status) {
    let color = '';
    switch(status) {
        case '待审核':
            color = 'orange';
            break;
        case '已批准':
            color = 'green';
            break;
        case '已拒绝':
            color = 'red';
            break;
        default:
            color = 'black';
    }
    return `<span style="color: ${color};">${status}</span>`;
}

// 显示结果消息
function showResult(elementId, message, isSuccess) {
    const resultElement = document.getElementById(elementId);
    resultElement.textContent = message;
    resultElement.style.display = 'block';
    resultElement.style.backgroundColor = isSuccess ? '#4CAF50' : '#f44336';
    resultElement.style.color = 'white';
    
    // 3秒后隐藏消息
    setTimeout(() => {
        resultElement.style.display = 'none';
    }, 3000);
}