// 登录页面JavaScript

// 表单提交处理
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // 阻止表单默认提交
    
    // 获取表单数据
    const job_id = document.getElementById('job_id').value;
    const password = document.getElementById('password').value;
    
    // 简单的表单验证
    if (!job_id || !password) {
        showError('工号和密码不能为空');
        return;
    }
    
    // 隐藏之前的错误信息
    hideError();
    
    // 模拟登录请求（实际项目中这里会发送AJAX请求到后端）
    const formData = new FormData();
    formData.append('job_id', job_id);
    formData.append('password', password);
    
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('登录请求失败');
        }
        return response.text();
    })
    .then(html => {
        // 因为后端处理后会重定向，所以这里的代码可能不会执行
        // 但为了完整性保留
        document.body.innerHTML = html;
    })
    .catch(error => {
        showError('登录失败：' + error.message);
    });
});

// 显示错误信息
function showError(message) {
    let errorElement = document.querySelector('.error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        const form = document.getElementById('loginForm');
        form.parentNode.insertBefore(errorElement, form.nextSibling);
    }
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// 隐藏错误信息
function hideError() {
    const errorElement = document.querySelector('.error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}