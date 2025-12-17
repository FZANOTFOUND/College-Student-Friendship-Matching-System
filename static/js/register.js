document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('sendCodeBtn');
    btn.addEventListener('click', function () {
        const email = document.getElementById('email').value.trim();
        fetch(`/api/account/code/email?email=${encodeURIComponent(email)}`)
            .then(res => res.json())
            .then(data => {
                if (data.code === 200) {

                } else {
                    showErrors(data.errors);
                }
            })
            .catch(err => {
                clearContainer();
                console.error(err);
                insertContainer("danger", "验证码获取失败");
            });
        })
});


document.getElementById('registerForm').addEventListener('submit', function (e) {
    e.preventDefault();
    clearContainer();


    const email = document.getElementById('email').value.trim();
    const code = document.getElementById('code').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const gender = document.getElementById('gender').value;
    const age = Number(document.getElementById('age').value);

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = '注册中...';

    fetch(this.action, {
        method: 'POST',
        body: new FormData(this),
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
        .then(r => r.json())
        .then(data => {
            console.log(data);
            if(data.code === 200){
                clearContainer();
                window.location.href = '/account/login';
                insertContainer("info", "注册成功，请登录");
            }
            else if(data.code === 400){
                showErrors(data.errors);
            }
            else{
                clearContainer();
                insertContainer("danger", "注册失败（服务器错误）");
            }
        })
        .catch(err => {
            clearContainer();
            console.error(err);
            insertContainer("danger", "注册失败（浏览器错误）");
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = '注册';
        });
});
