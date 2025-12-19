document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    clearContainer();


    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').value;

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = '登录中...';

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
            if(data.code === 200 || data.code === 201 ){
                clearContainer();
                //setLocalStorage(data.data);
                window.location.href = '/';
            }
            else if(data.code === 400){
                showErrors(data.errors);
            }
            else{
                clearContainer();
                insertContainer("danger", "登录失败（服务器错误）");
            }
        })
        .catch(err => {
            clearContainer();
            console.error(err);
            insertContainer("danger", "登录失败（浏览器错误）");
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = '登录';
        });
});