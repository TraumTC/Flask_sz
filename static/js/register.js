// 注册页面JavaScript

// 表单提交处理
document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault(); // 阻止表单默认提交
    
    // 获取表单数据
    const job_id = document.getElementById('job_id').value;
    const name = document.getElementById('name').value;
    const password = document.getElementById('password').value;
    const gender = document.getElementById('gender').value;
    const duty = document.getElementById('duty').value;
    
    // 简单的表单验证
    if (!job_id || !name || !password || !gender || !duty) {
        showError('所有字段不能为空');
        return;
    }
    
    // 隐藏之前的错误信息
    hideError();
    
    // 模拟注册请求
    const formData = new FormData();
    formData.append('job_id', job_id);
    formData.append('name', name);
    formData.append('password', password);
    formData.append('gender', gender);
    formData.append('duty', duty);
    
    fetch('/register', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('注册请求失败');
        }
        return response.text();
    })
    .then(html => {
        // 注册成功后，后端会重定向到登录页面
        document.body.innerHTML = html;
    })
    .catch(error => {
        showError('注册失败：' + error.message);
    });
});

// 显示错误信息
function showError(message) {
    let errorElement = document.querySelector('.error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        const form = document.getElementById('registerForm');
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