function get(obj, key, defaultValue) {
    return obj.hasOwnProperty(key) ? obj[key] : defaultValue;
}

function clearContainer(){
    const container = document.getElementById('container-inner');
    container.innerHTML = '';
}

function setLocalStorage(data) {
    for(let key in data){
        let value = data[key];
        localStorage.setItem(key, value);
    }
}

function logout_client(){
    clearContainer();
    clearLocalStorage();
}

function getCookie(name) {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1];
}

function handleLogout() {

    fetch("/api/account/logout",{
        method: 'POST',
        credentials: "include",
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        }})
        .finally(() => {
            logout_client();
            window.location.href = '/';
        });
}
function clearLocalStorage(){
    localStorage.clear();
}

function showErrors(errors, limit=1){
    clearContainer();
    let cnt = 0;
    Object.keys(errors??[]).forEach((key) => {
        const errorList = errors[key];
        if (!Array.isArray(errorList)) return;

        errorList.forEach((errorMsg) => {
            if(cnt < limit) {
                insertContainer("warning", errorMsg);
                console.log("cnt:"+cnt);
            }
            cnt++;
        });
    });
}
function insertContainer(category, message) {
    category = category.toLowerCase();
    const container = document.getElementById('container-inner');
    // console.log(container);
    const el = document.createElement('div');
    el.className = 'alert alert-dismissible fade show'
    el.setAttribute('role', 'alert');
    if(category === 'warning' || category === 'success' || category === 'danger'){
        el.classList.add(`alert-${category}`);
    }
    else{
        el.classList.add(`alert-info`);
    }
    el.textContent = message;
    el.innerHTML += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">'
    container.appendChild(el);
}

async function checkLogin() {
    const resp = await fetch("/api/account/profile", {
        credentials: "include"
    }).then(r => r.json());

    if (resp.code === 200) {
        return { loggedIn: true, data: resp.data };
    } else {
        return { loggedIn: false };
    }
}

async function apiFetch(path, options) {
    options = options || {};
    options.headers = options.headers || {};
    options.headers["X-CSRF-TOKEN"] = getCookie("csrf_access_token");
    options["credentials"] =  "include";
    const res = await fetch(path, options);
    const json = await res.json();
    console.log(json);
    if (json.code !== 200 && json.code !== 201) {
      throw json;
    }
    return json;
}
function loadUnreadNotificationCount() {
    const badge = document.getElementById('notification-badge');
    if (!badge) return;

    fetch("/api/notification/unread/count", {
        method: "GET",
        credentials: "include"
    })
        .then(r => r.json())
        .then(data => {
            if (data.code !== 200 && data.code !== 201) return;

            const count = data.data.count;
            if (count > 0) {
                badge.textContent = count > 99 ? "99+" : count;
                badge.style.display = "inline-block";
            } else {
                badge.style.display = "none";
            }
        })
        .catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
    const navMenu = document.getElementById("navMemu");
    if(navMenu === null){
        console.log("Waring no navMemu");
        return;
    }
    navMenu.innerHTML = '';
    checkLogin().then(res => {
        const isAuthenticated = res.loggedIn;
            if (isAuthenticated) {
            // 通知界面链接
            const notifications = document.createElement('li');
            notifications.className = 'nav-item';
            notifications.innerHTML = notifications.innerHTML = `
                <a class="nav-link position-relative" href="/notifications/">
                    📢
                    <span id="notification-badge"
                          class="position-absolute top-2 start-100 translate-middle badge rounded-pill bg-danger"
                          style="
                            display:none;
                            font-size: 0.65rem;
                            padding: 0.2em 0.4em;
                            min-width: 1.2em;
                          "">
                    </span>
                </a>
            `;
            navMenu.appendChild(notifications);

            // 个人界面链接
            const profileItem = document.createElement('li');
            profileItem.className = 'nav-item';
            profileItem.innerHTML = '<a class="nav-link" href="/account/protected">个人界面</a >';
            navMenu.appendChild(profileItem);

            // 登出链接
            const logoutItem = document.createElement('li');
            logoutItem.className = 'nav-item';
            logoutItem.innerHTML = '<a class="nav-link" href="#" id="logoutBtn">登出</a >';
            navMenu.appendChild(logoutItem);

            // 绑定登出事件
            document.getElementById('logoutBtn').addEventListener('click', handleLogout);

            loadUnreadNotificationCount();
        }
        else {
            // 未登录：渲染「登录」和「注册」
            // 登录链接
            const loginItem = document.createElement('li');
            loginItem.className = 'nav-item';
            loginItem.innerHTML = '<a class="nav-link" href="/account/login">登录</a >';
            navMenu.appendChild(loginItem);

            // 注册链接
            const registerItem = document.createElement('li');
            registerItem.className = 'nav-item';
            registerItem.innerHTML = '<a class="nav-link" href="/account/register">注册</a >';
            navMenu.appendChild(registerItem);
        }
        console.log("base ok");
    });

});
