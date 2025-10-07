// 管理员主页JavaScript

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', function() {
    // 初始化标签页
    initTabs();
    
    // 绑定员工搜索按钮事件
    document.getElementById('searchEmployeeBtn').addEventListener('click', searchEmployees);
    
    // 绑定考勤统计查询按钮事件
    document.getElementById('generateReportBtn').addEventListener('click', searchAttendanceReport);
    
    // 绑定导出报表按钮事件
    document.getElementById('exportCsvBtn').addEventListener('click', exportReport);
    
    // 初始化当前月份
    const today = new Date();
    const currentMonth = today.toISOString().slice(0, 7);
    document.getElementById('reportMonth').value = currentMonth;
    document.getElementById('exportMonth').value = currentMonth;
    
    // 绑定分页按钮事件
    document.getElementById('prevPage').addEventListener('click', goToPrevPage);
    document.getElementById('nextPage').addEventListener('click', goToNextPage);
    
    // 默认加载员工列表
    loadEmployees();
});

// 全局变量存储当前页码和每页条数
let currentPage = 1;
let perPage = 10;

// 初始化标签页
function initTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有标签的活动状态
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加当前标签的活动状态
            this.classList.add('active');
            
            // 显示对应的内容
            const target = this.getAttribute('data-tab');
            document.getElementById(target + 'Tab').classList.add('active');
            
            // 根据标签加载对应数据
            if (target === 'employee') {
                loadEmployees();
            } else if (target === 'attendance') {
                searchAttendanceReport();
            } else if (target === 'leave') {
                loadLeaveRequests();
            }
        });
    });
}

// 加载员工列表
function loadEmployees() {
    const keyword = document.getElementById('employeeSearch').value || '';
    fetch(`/api/admin/employees?page=${currentPage}&per_page=${perPage}&search=${keyword}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('加载员工列表失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderEmployeesTable(data.data.employees);
            // 更新分页信息
            document.getElementById('pageInfo').textContent = `第 ${data.data.page} 页，共 ${data.data.pages} 页`;
            
            // 更新当前页码
            currentPage = data.data.page;
            
            // 禁用/启用分页按钮
            document.getElementById('prevPage').disabled = data.data.page <= 1;
            document.getElementById('nextPage').disabled = data.data.page >= data.data.pages;
        } else {
            showResult('employeesResult', data.message, false);
        }
    })
    .catch(error => {
        showResult('employeesResult', '加载员工列表失败：' + error.message, false);
    });
}

// 上一页
function goToPrevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadEmployees();
    }
}

// 下一页
function goToNextPage() {
    loadEmployees();
}

// 搜索员工
function searchEmployees() {
    const keyword = document.getElementById('employeeSearch').value;
    
    fetch(`/api/admin/employees?search=${keyword}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('搜索员工失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderEmployeesTable(data.data.employees);
            // 更新分页信息
            document.getElementById('pageInfo').textContent = `第 ${data.data.page} 页，共 ${data.data.pages} 页`;
        } else {
            showResult('employeesResult', data.message, false);
        }
    })
    .catch(error => {
        showResult('employeesResult', '搜索员工失败：' + error.message, false);
    });
}

// 渲染员工表格
function renderEmployeesTable(employees) {
    const tableBody = document.getElementById('employeeTableBody');
    tableBody.innerHTML = '';
    
    if (employees.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6" style="text-align: center;">暂无员工数据</td>';
        tableBody.appendChild(emptyRow);
        return;
    }
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${employee.job_id || '-'}</td>
            <td>${employee.name || '-'}</td>
            <td>${employee.gender || '-'}</td>
            <td>${employee.duty || '-'}</td>
            <td>${employee.is_admin ? '是' : '否'}</td>
            <td>
                <button class="edit-btn" data-id="${employee.job_id}">编辑</button>
                <button class="delete-btn" data-id="${employee.job_id}">删除</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // 绑定编辑和删除按钮事件
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const jobId = this.getAttribute('data-id');
            editEmployee(jobId);
        });
    });
    
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const jobId = this.getAttribute('data-id');
            if (confirm(`确定要删除工号为 ${jobId} 的员工吗？`)) {
                deleteEmployee(jobId);
            }
        });
    });
}

// 编辑员工
function editEmployee(jobId) {
    // 这里可以打开编辑模态框，获取员工信息并填充表单
    // 为简化示例，这里只显示一个提示
    showResult('employeesResult', '编辑功能待实现', true);
}

// 删除员工
function deleteEmployee(jobId) {
    fetch(`/api/admin/employees/${jobId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('删除员工失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('employeesResult', data.message, data.code === 200);
        if (data.code === 200) {
            // 删除成功后重新加载员工列表
            loadEmployees();
        }
    })
    .catch(error => {
        showResult('employeesResult', '删除员工失败：' + error.message, false);
    });
}

// 搜索考勤报表
function searchAttendanceReport() {
    const month = document.getElementById('reportMonth').value;
    
    if (!month) {
        showResult('attendanceResult', '请选择月份', false);
        return;
    }
    
    fetch(`/api/attendance_report?month=${month}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('获取考勤报表失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderAttendanceReport(data.data);
        } else {
            showResult('attendanceResult', data.message, false);
        }
    })
    .catch(error => {
        showResult('attendanceResult', '获取考勤报表失败：' + error.message, false);
    });
}

// 渲染考勤报表
function renderAttendanceReport(report) {
    const tableBody = document.getElementById('attendanceReportTableBody');
    tableBody.innerHTML = '';
    
    if (report.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="8" style="text-align: center;">暂无考勤数据</td>';
        tableBody.appendChild(emptyRow);
        return;
    }
    
    report.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.job_id || '-'}</td>
            <td>${record.name || '-'}</td>
            <td>${record.work_days || 0}</td>
            <td>${record.normal_count || 0}</td>
            <td>${record.late_count || 0}</td>
            <td>${record.early_leave_count || 0}</td>
            <td>${record.absenteeism_count || 0}</td>
            <td>${record.leave_count || 0}</td>
        `;
        tableBody.appendChild(row);
    });
}

// 加载请假申请
function loadLeaveRequests() {
    fetch('/api/admin/leave_requests')
    .then(response => {
        if (!response.ok) {
            throw new Error('加载请假申请失败');
        }
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            renderLeaveRequests(data.data);
        }
    })
    .catch(error => {
        console.error('加载请假申请失败：', error);
    });
}

// 渲染请假申请表格
function renderLeaveRequests(requests) {
    const tableBody = document.getElementById('leaveApprovalTableBody');
    tableBody.innerHTML = '';
    
    if (requests.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6" style="text-align: center;">暂无请假申请</td>';
        tableBody.appendChild(emptyRow);
        return;
    }
    
    requests.forEach(request => {
        const row = document.createElement('tr');
        let actions = '';
        
        if (request.status === '待审核') {
            actions = `
                <button class="approve-btn" data-id="${request.id}">批准</button>
                <button class="reject-btn" data-id="${request.id}">拒绝</button>
            `;
        }
        
        row.innerHTML = `
            <td>${request.application_time || '-'}</td>
            <td>${request.employee_name || '-'}</td>
            <td>${request.reason || '-'}</td>
            <td>${request.days || '-'}</td>
            <td>${getStatusColor(request.status || '-')}</td>
            <td>${actions}</td>
        `;
        tableBody.appendChild(row);
    });
    
    // 绑定批准和拒绝按钮事件
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const leaveId = this.getAttribute('data-id');
            approveLeave(leaveId);
        });
    });
    
    document.querySelectorAll('.reject-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const leaveId = this.getAttribute('data-id');
            rejectLeave(leaveId);
        });
    });
}

// 批准请假
function approveLeave(leaveId) {
    fetch(`/api/leave/${leaveId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: '已批准' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('批准请假失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('leaveResult', data.message, data.code === 200);
        if (data.code === 200) {
            loadLeaveRequests();
        }
    })
    .catch(error => {
        showResult('leaveResult', '批准请假失败：' + error.message, false);
    });
}

// 拒绝请假
function rejectLeave(leaveId) {
    fetch(`/api/leave/${leaveId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: '已拒绝' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('拒绝请假失败');
        }
        return response.json();
    })
    .then(data => {
        showResult('leaveResult', data.message, data.code === 200);
        if (data.code === 200) {
            loadLeaveRequests();
        }
    })
    .catch(error => {
        showResult('leaveResult', '拒绝请假失败：' + error.message, false);
    });
}

// 导出报表
function exportReport() {
    const month = document.getElementById('exportMonth').value;
    
    if (!month) {
        showResult('exportResult', '请选择导出月份', false);
        return;
    }
    
    // 打开新窗口下载报表
    window.open(`/api/export_report?month=${month}`, '_blank');
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