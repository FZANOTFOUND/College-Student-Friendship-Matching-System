let myUserId = null;
let currentConvId = null;

/* ================= API ================= */
async function apiFetch(path, options = {}) {
  options.credentials = "include";
  options.headers = options.headers || {};
  options.headers["X-CSRF-TOKEN"] =
    document.cookie.split("; ")
      .find(r => r.startsWith("csrf_access_token="))
      ?.split("=")[1];

  const res = await fetch(path, options);
  const json = await res.json();
  if (json.code !== 200 && json.code !== 201) {
    throw json;
  }
  return json;
}

/* ================= 时间格式 ================= */
function formatTime(iso) {
  return new Date(iso).toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

/* ================= 当前用户 ================= */
async function loadMyProfile() {
  const res = await apiFetch("/api/account/profile");
  myUserId = res.data.user_id;
}

async function selectConversation(convId, title) {
  currentConvId = convId;
  document.getElementById("chat-title").textContent = title;
  await loadMessages();
}

/* ================= 会话列表 ================= */
function loadConversations() {
  apiFetch("/api/conversations/all").then(res => {
    const list = document.getElementById("conversation-list");
    list.innerHTML = "";

    res.data.forEach(conv => {
      const div = document.createElement("div");
      div.className = "conversation-item";

      const name = conv.participants.map(p => p.username).join(", ");
      div.innerHTML = `
        <strong>${name}</strong><br>
        <small>${conv.last_message || "暂无消息"}</small>
        ${conv.unread_count > 0 ? `<span class="text-danger"> (${conv.unread_count})</span>` : ""}
      `;

      div.onclick = () => {
        document.querySelectorAll(".conversation-item")
          .forEach(i => i.classList.remove("active"));
        div.classList.add("active");

        currentConvId = conv.conv_id;
        document.getElementById("chat-title").textContent = name;
        loadMessages();
      };

      list.appendChild(div);
    });
  });
}

/* ================= 消息 ================= */
function loadMessages() {
  apiFetch(`/api/conversations/${currentConvId}/messages`).then(res => {
    const box = document.getElementById("message-list");
    box.innerHTML = "";

    res.data.forEach(msg => {
      const wrap = document.createElement("div");
      wrap.className =
        "chat-message " + (msg.sender_id === myUserId ? "me" : "other");

      const bubble = document.createElement("div");
      bubble.className = "chat-bubble";
      bubble.textContent = msg.content;

      const time = document.createElement("div");
      time.className = "chat-time";
      time.textContent = formatTime(msg.sent_at);

      bubble.appendChild(time);
      wrap.appendChild(bubble);
      box.appendChild(wrap);
    });

    box.scrollTop = box.scrollHeight;
    loadConversations();
  });
}

/* ================= 发送 ================= */
function sendMessage() {
  const input = document.getElementById("message-input");
  const content = input.value.trim();
  if (!content || !currentConvId) return;

  apiFetch(`/api/conversations/${currentConvId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  }).then(() => {
    input.value = "";
    loadMessages();
  });
}

async function startConversation(userId, username) {
  const res = await apiFetch("/api/conversations/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipient_id: userId })
  });

  const convId = res.data.conv_id;

  // 重新加载会话列表
  await loadConversations();

  // 自动打开该会话
  selectConversation(convId, username);
}

/* ================= 推荐用户 ================= */
async function loadRecommendUsers() {
  const res = await apiFetch("/api/tags/recommend");

  const list = document.getElementById("recommend-list");
  list.innerHTML = "";

  res.data.forEach(user => {
    const div = document.createElement("div");
    div.className = "recommend-user d-flex justify-content-between align-items-center";

    div.innerHTML = `
      <div>
        <strong>${user.username}</strong>
        <div class="text-muted" style="font-size: 0.8rem">
          相似度 ${user.similarity}
        </div>
      </div>
      <button class="btn btn-sm btn-outline-primary">
        私信
      </button>
    `;

    // 私信按钮事件
    div.querySelector("button").addEventListener("click", () => {
      startConversation(user.user_id, user.username);
    });

    list.appendChild(div);
  });
}

/* ================= 初始化 ================= */
document.getElementById("send-btn").onclick = sendMessage;
document.getElementById("message-input").addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

document.addEventListener("DOMContentLoaded", async () => {
  await loadMyProfile();        // ⭐ 唯一身份来源
  loadConversations();
  loadRecommendUsers();
});
