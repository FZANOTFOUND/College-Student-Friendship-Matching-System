let allNotifications = [];   // 后端返回的完整数据
let currentStatus = 'unread';
let currentPage = 1;
const perPage = 10;

/* ================= 拉取全部通知 ================= */
function fetchAllNotifications() {
  document.getElementById('mark-all-read').onclick = markAllAsRead;
  fetch(`/api/notification/all?page=1&per_page=1000`) // 拉大一点
    .then(res => res.json())
    .then(res => {
      if (res.code !== 200) {
        alert('获取通知失败');
        return;
      }
      allNotifications = res.data.items;
      render();
    });
}

/* ========== 一键全部已读 ========== */
function markAllAsRead() {
  if (!allNotifications.some(n => !n.is_read)) {
    alert('没有未读通知');
    return;
  }

  if (!confirm('确定将所有通知标记为已读？')) return;

  fetch('/api/notification/all/read', {
    method: 'PUT',
    headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
    }
  })
    .then(res => res.json())
    .then(res => {
      if (res.code === 200) {
        // 本地同步状态
        allNotifications.forEach(n => n.is_read = true);
        render();
      } else {
        alert(res.message || '操作失败');
      }
    });
}

/* ================= 过滤 + 分页 ================= */
function getFilteredList() {
  if (currentStatus === 'unread') {
    return allNotifications.filter(n => !n.is_read);
  }
  if (currentStatus === 'read') {
    return allNotifications.filter(n => n.is_read);
  }
  return allNotifications;
}

function getPagedList(list) {
  const start = (currentPage - 1) * perPage;
  return list.slice(start, start + perPage);
}

/* ================= 渲染 ================= */
function render() {
  const filtered = getFilteredList();
  const paged = getPagedList(filtered);
  renderNotifications(paged);
  renderPagination(filtered.length);
  loadUnreadNotificationCount();
}

function renderNotifications(items) {
  const container = document.getElementById('notification-list');
  container.innerHTML = '';

  if (items.length === 0) {
    container.innerHTML = `<div class="text-muted">暂无通知</div>`;
    return;
  }

  items.forEach(n => {
    const div = document.createElement('div');
    div.className = `list-group-item ${n.is_read ? '' : 'list-group-item-warning'}`;

    div.innerHTML = `
      <div class="d-flex justify-content-between">
        <h6>${getTypeText(n.type)}</h6>
        <small>${formatTime(n.created_at)}</small>
      </div>
      <p class="mb-2">${n.content}</p>
      <div class="d-flex justify-content-between align-items-center">
        
        ${
          n.is_read
            ? `<span class="badge bg-secondary">已读</span>`
            : `<button class="btn btn-sm btn-success" onclick="markAsRead(${n.notify_id})">标记已读</button>`
        }
      </div>
    `;
    container.appendChild(div);
  });
}

/* ================= 标记已读 ================= */
function markAsRead(notifyId) {
  fetch(`/api/notification/${notifyId}/read`, {
    method: 'PUT',
    headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
    }
  })
    .then(res => res.json())
    .then(res => {
      if (res.code === 200) {
        const n = allNotifications.find(x => x.notify_id === notifyId);
        if (n) n.is_read = true;
        render();
      } else {
        alert(res.message || '操作失败');
      }
    });
}

/* ================= 分页 ================= */
function renderPagination(total) {
  const pagination = document.getElementById('pagination');
  pagination.innerHTML = '';
  const totalPages = Math.ceil(total / perPage);

  for (let i = 1; i <= totalPages; i++) {
    const li = document.createElement('li');
    li.className = `page-item ${i === currentPage ? 'active' : ''}`;

    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = '#';
    a.innerText = i;
    a.onclick = (e) => {
      e.preventDefault();
      currentPage = i;
      render();
    };

    li.appendChild(a);
    pagination.appendChild(li);
  }
}

/* ================= 筛选按钮 ================= */
function setActive(id) {
  document.querySelectorAll('.btn-group button')
    .forEach(btn => btn.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

document.getElementById('filter-unread').onclick = () => {
  currentStatus = 'unread';
  currentPage = 1;
  setActive('filter-unread');
  render();
};

document.getElementById('filter-all').onclick = () => {
  currentStatus = 'all';
  currentPage = 1;
  setActive('filter-all');
  render();
};

document.getElementById('filter-read').onclick = () => {
  currentStatus = 'read';
  currentPage = 1;
  setActive('filter-read');
  render();
};

/* ================= 工具函数 ================= */
function getTypeText(type) {
  type = type.toLocaleLowerCase();
  return {
    comment: '💬 评论',
    like: '👍 点赞',
    system: '⚙️ 系统'
  }[type] || '📢 通知';
}

function formatTime(iso) {
  return new Date(iso).toLocaleString();
}

document.addEventListener('DOMContentLoaded', fetchAllNotifications);
