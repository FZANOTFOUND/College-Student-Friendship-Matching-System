// static/codeforces_rank.js

function get(obj, key, defaultValue) {
    return obj.hasOwnProperty(key) ? obj[key] : defaultValue;
}

document.addEventListener("DOMContentLoaded", () => {
    // const container = document.querySelector('#user-show');
    // const el = document.createElement('div');
    // el.textContent = username + " Error:" + info.msg;
    // 设置属性
    // el.setAttribute('title', username);
    // container.appendChild(el);
    const out = document.getElementById('output');
    const tbody = document.getElementById('tbody');
    const refreshBtn = document.getElementById('refreshBtn');
    const forceRefreshBtn = document.getElementById('forceRefreshBtn');
    out.textContent = '加载中：';
    function setButtonsDisabled(disabled) {
        refreshBtn.disabled = disabled;
        forceRefreshBtn.disabled = disabled;
    }
    async function fetchData(use_cache=true) {
        setButtonsDisabled(true);
        try {
            while (tbody.firstChild) {
                tbody.removeChild(tbody.firstChild);
            }
            console.log(`/api/codeforces/data?use_cache=${use_cache}`);
            const res = await fetch(`/api/codeforces/data?use_cache=${use_cache}`); // GET 请求
            if (!res.ok) {
                out.textContent = '加载失败：' + res.status;
            } else {
                const data = await res.json(); // 等待返回 JSON
                let ok = 0, wa = 0;

                if (!get(data, "ok", false)) {
                    out.textContent = '加载失败：' + get(data, "msg", "server_no_data");
                } else {
                    // 遍历 data.data
                    data.data.sort((a, b) =>{
                        const userA = a[Object.keys(a)[0]];
                        const userB = b[Object.keys(b)[0]];

                        const ra = Number(userA.rating) || 0;
                        const rb = Number(userB.rating) || 0;

                        return rb - ra; // 从高到低
                    });
                    (data.data ?? []).forEach(item => {
                        // 每个 item 是只有一个键的对象：用户名
                        const [username, info] = Object.entries(item)[0];
                        if(get(info, "status", "ERROR").toLowerCase() !==  "OK".toLowerCase()) {
                            wa ++;
                            console.log("Error:" + username + " " + info.msg);
                        }
                        else{
                            ok++;
                            console.log("adding " + username);
                            if(info.rating >= 3000){
                                // 大于 3000 的 rating 显示首字母和后续字母的颜色不同
                                const tr = document.createElement("tr");
                                const a1 = document.createElement("a");
                                const td2 = document.createElement("td");
                                const td3 = document.createElement("td");
                                const span = document.createElement("span");
                                a1.href = `https://codeforces.com/profile/${username}`
                                a1.title = username;
                                a1.target = "_blank";
                                a1.rel = "noopener noreferrer";
                                span.textContent = username[0];
                                td2.textContent = info.rank;
                                td3.textContent = info.rating;
                                if(info.rating >= 4000){
                                    span.className = "user-4000-first-letter";
                                    a1.className = "bold user-4000";
                                    td2.className = "red";
                                    td3.className = "user-red";
                                }
                                else{
                                    span.className = "legendary-user-first-letter";
                                    a1.className = "bold user-legendary";
                                    td2.className = "user-red";
                                    td3.className = "user-red";
                                }
                                a1.classList.add("no-underline")
                                a1.appendChild(span);
                                a1.appendChild(document.createTextNode(username.slice(1)))

                                const td1 = document.createElement("td");
                                td1.appendChild(a1);
                                tr.appendChild(td1);
                                tr.appendChild(td2);
                                tr.appendChild(td3);
                                tbody.appendChild(tr);
                            }
                            else{
                                // 所有的字母都是同一个颜色
                                const tr = document.createElement("tr");
                                const a1 = document.createElement("a");
                                const td2 = document.createElement("td");
                                const td3 = document.createElement("td");
                                a1.href = `https://codeforces.com/profile/${username}`
                                a1.title = username;
                                a1.textContent = username;
                                a1.target = "_blank";
                                a1.rel = "noopener noreferrer";
                                td2.textContent = info.rank;
                                td3.textContent = info.rating
                                if(info.rating>= 2400){
                                    a1.className = "bold user-red";
                                    td2.className = "user-red"
                                    td3.className = "user-red";
                                }
                                else if (info.rating >= 2100){
                                    a1.className = "bold user-orange";
                                    td2.className = "user-orange"
                                    td3.className = "user-orange";
                                }
                                else if(info.rating >= 1900){
                                    a1.className = 'bold user-violet';
                                    td2.className = "user-violet"
                                    td3.className = "user-violet";
                                }
                                else if(info.rating >= 1600){
                                    a1.className = 'bold user-blue';
                                    td2.className = "user-blue"
                                    td3.className = "user-blue";
                                }
                                else if(info.rating >= 1400) {
                                    a1.className = 'bold user-cyan';
                                    td2.className = "user-cyan"
                                    td3.className = "user-cyan";
                                }
                                else if(info.rating >= 1200){
                                    a1.className = 'bold user-green';
                                    td2.className = "user-green"
                                    td3.className = "user-green";
                                }
                                else if(info.rating > 0){
                                    a1.className = 'bold user-gray';
                                    td2.className = "user-gray"
                                    td3.className = "user-gray";
                                }
                                else{
                                    a1.className = 'user-black';
                                    td2.className = "user-black"
                                    td3.className = "user-black";
                                }
                                a1.classList.add("no-underline")
                                // 插入元素
                                const td1 = document.createElement("td");
                                td1.appendChild(a1);
                                tr.appendChild(td1);
                                tr.appendChild(td2);
                                tr.appendChild(td3);
                                tbody.appendChild(tr);
                            }

                        }


                    });

                    // 把 JSON 格式化输出
                    // out.textContent = JSON.stringify(data, null, 2);
                    const date = new Date(data.data_time*1000);
                    const formatted = date.toLocaleString();
                    out.textContent = "加载完毕：共 " + (ok+wa) + " 条 / "+wa+" 条失败";

                }

            }
        } catch (err) {
            out.textContent = '加载失败：' + err.message;
            console.error(err);
        }
        setButtonsDisabled(false);
    }

    fetchData(true);

    // 事件：常规刷新（优先使用缓存）
    refreshBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fetchData(true);
    });

    // 事件：强制刷新（从远程抓取，use_cache=0）
    forceRefreshBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!confirm("确定要强制从远程抓取最新数据并更新缓存吗？此操作会向目标站点发起请求，可能较慢。")) {
            return;
        }
        await fetchData(false);
        // 可选：对用户做进一步提示
        console.log("强制刷新操作完成");
    });
});
