document.addEventListener("DOMContentLoaded", () => {
    const cardMenu = document.getElementById("cardMenu");
    console.log(cardMenu);
    if (cardMenu === null) {
        console.log("Warning no cardMenu");
        return;
    }
    cardMenu.innerHTML = '';


    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'null';
    const email = localStorage.getItem('email') || 'null';
    const isAuthenticated = !!token && !!username;


    const cardTitle = document.createElement('h4');
    const cardText = document.createElement('p');
    const a1 = document.createElement('a');



    cardTitle.className = 'card-title';
    cardText.className = 'card-text';
    a1.className = 'btn btn-primary me-2';

    if (isAuthenticated) {
        cardTitle.textContent = `欢迎回来, ${username || '用户'} 👋`;
        cardText.innerHTML = `您已使用 <strong>${email || ''}</strong> 登录.`; // 保留加粗样式

        a1.href = '/account/protected';

        a1.textContent = '个人界面';
    } else {
        cardTitle.textContent = "欢迎访问 神秘数据库大作业";
        cardText.textContent = "纳西妲世界第一可爱！！！";

        a1.href = '/account/login';

        a1.textContent = '登录';

    }
    cardMenu.appendChild(cardTitle);
    cardMenu.appendChild(cardText);
    cardMenu.appendChild(a1);
    if(isAuthenticated) {
        const a2 = document.createElement('button');
        a2.className = 'btn btn-outline-secondary';
        a2.textContent = '登出';
        a2.addEventListener('click', () => {

            fetch("/api/account/logout",{
            method: 'POST',

            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'Authorization': "Bearer " + localStorage.getItem('token'),
            }})
                .finally()
            {
                logout_client();
                location.reload();
            }

        })
        cardMenu.appendChild(a2);
    }
    else{
        const a2 = document.createElement('a');
        a2.className = 'btn btn-success';
        a2.href = '/account/register';
        a2.textContent = '注册';
        cardMenu.appendChild(a2);
    }



    console.log("ok");
});