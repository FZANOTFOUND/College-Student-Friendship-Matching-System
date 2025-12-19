const API_URL = "/api/admin/query/time_period";


/* ---------- 辅助格式函数（本地时间、无毫秒、无 Z） ---------- */
function pad2(n){ return String(n).padStart(2, '0'); }
function pad4(n){ return String(n).padStart(4, '0'); }

function formatLocalNoMs(date) {
    // 使用本地时间分量，输出 YYYY-MM-DDTHH:MM:SS（不含时区标识）
    const Y = pad4(date.getFullYear());
    const M = pad2(date.getMonth() + 1);
    const D = pad2(date.getDate());
    const h = pad2(date.getHours());
    const m = pad2(date.getMinutes());
    const s = pad2(date.getSeconds());
    return `${Y}-${M}-${D}T${h}:${m}:${s}Z`;
}

/* ---------- 计算时间范围（全部按本地时间） ---------- */
function calcRange(type) {
    const now = new Date(); // 本地时间
    let start;

    switch(type) {
        case "all":
            // 保持四位年份
            return { start: "0001-01-01T00:00:00Z", end: formatLocalNoMs(now) };

        case "1y":
            start = new Date(now);
            start.setFullYear(start.getFullYear() - 1);
            break;

        case "6m":
            start = new Date(now);
            start.setMonth(start.getMonth() - 6);
            break;

        case "3m":
            start = new Date(now);
            start.setMonth(start.getMonth() - 3);
            break;

        case "1m":
            start = new Date(now);
            start.setMonth(start.getMonth() - 1);
            break;

        case "2w":
            start = new Date(now.getTime() - 14 * 86400 * 1000);
            break;

        case "1w":
            start = new Date(now.getTime() - 7 * 86400 * 1000);
            break;

        case "today":
            start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            break;

        default:
            return { start: "0001-01-01T00:00:00Z", end: formatLocalNoMs(now) };
    }

    return { start: formatLocalNoMs(start), end: formatLocalNoMs(now) };
}

/* ---------- 渲染列表 ---------- */
function renderList(el, users) {
    el.innerHTML = "";
    if (!users || users.length === 0) {
        el.innerHTML = `<li class="list-group-item text-muted">无数据</li>`;
        return;
    }
    users.forEach(u => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = `#${u.user_id} - ${u.username}`;
        el.appendChild(li);
    });
}

/* ---------- 加载数据（发送本地时间字符串） ---------- */
function loadData(rangeType) {
    const { start, end } = calcRange(rangeType);

    // 注意：这里发送的 start/end 是本地时间字符串（无时区）
    const url = `${API_URL}?start_time=${encodeURIComponent(start)}&end_time=${encodeURIComponent(end)}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (!data || data.code !== 200) {
                alert("查询失败");
                return;
            }

            // 兼容命名
            const newUsers = data.new_users || data.newUsers || [];
            const loginUsers = data.login_users || data.loginUsers || [];

            document.getElementById("newCount").innerText = newUsers.length;
            document.getElementById("loginCount").innerText = loginUsers.length;

            renderList(document.getElementById("newUserList"), newUsers);
            renderList(document.getElementById("loginUserList"), loginUsers);
        })
        .catch(err => {
            console.error(err);
            alert("请求异常：" + (err && err.message));
        });
}

/* ---------- 初始化 ---------- */
document.addEventListener("DOMContentLoaded", () => {
    const select = document.getElementById("timeRange");
    if (!select) return;

    // 首次加载
    loadData(select.value);

    // 切换时间范围
    select.addEventListener("change", () => loadData(select.value));
});
