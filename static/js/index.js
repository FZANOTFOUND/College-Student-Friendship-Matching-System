document.addEventListener("DOMContentLoaded", () => {
    const cardMenu = document.getElementById("cardMenu");
    console.log(cardMenu);
    if (cardMenu === null) {
        console.log("Warning no cardMenu");
        return;
    }
    cardMenu.innerHTML = '';



    checkLogin().then(res => {
        //console.log(res);
        const isAuthenticated = res.loggedIn;


        const cardTitle = document.createElement('h4');
        const cardText = document.createElement('p');
        const a1 = document.createElement('a');



        cardTitle.className = 'card-title';
        cardText.className = 'card-text';
        a1.className = 'btn btn-primary me-2';

        console.log("是否登录：" + isAuthenticated);
        if (isAuthenticated) {
            const username = res.data.username || '';
            const email = res.data.email || '';
            const role = res.data.role || 0;
            if(role){
                cardTitle.textContent = `欢迎回来, 管理员 ${username || '用户'} 👋`;
            }
            else{
                cardTitle.textContent = `欢迎回来, 用户 ${username || '用户'} 👋`;
            }
            cardText.innerHTML = `您已使用 <strong>${email || ''}</strong> 登录.`; // 保留加粗样式


            a1.href = '/account/profile';

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
        if (isAuthenticated && (res.data.role || 0)) {
            const a0 = document.createElement('a');
            a0.className = 'btn btn-primary me-2';
            a0.href = '/admin';
            a0.textContent = '管理员界面';
            cardMenu.appendChild(a0);
        }
        if(isAuthenticated) {
            const a3 = document.createElement('a');
            const a4 = document.createElement('a');
            const a2 = document.createElement('button');
            a3.href = '/conversations'
            a3.textContent = '对话'
            a4.href = '/posts'
            a4.textContent = '帖子'
            a3.className = 'btn btn-primary me-2';
            a4.className = 'btn btn-primary me-2';
            a2.className = 'btn btn-outline-secondary';
            a2.textContent = '登出';
            a2.addEventListener('click', handleLogout)
            cardMenu.appendChild(a3);
            cardMenu.appendChild(a4);
            cardMenu.appendChild(a2);
        }
        else{
            const a2 = document.createElement('a');
            a2.className = 'btn btn-success';
            a2.href = '/account/register';
            a2.textContent = '注册';
            cardMenu.appendChild(a2);
        }
        console.log("index ok");
    });





});