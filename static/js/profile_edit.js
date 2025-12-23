/*
  profile_edit.js (inline)
  - 载入当前 profile（GET /api/account/profile）
  - 提交修改（PUT /api/account/profile/change）
  - 支持返回错误显示
  - 依赖 CSRF cookie 名称 csrf_access_token（与你现有 base.js 保持一致）
*/

// 如果全局已经有 apiFetch 或 getCookie 或 insertContainer / showErrors，我们优先使用它们
const globalApiFetch = window.apiFetch;
const globalGetCookie = window.getCookie;
const globalInsertContainer = window.insertContainer;
const globalShowErrors = window.showErrors;


async function localApiFetch(path, options = {}) {
  options = options || {};
  options.headers = options.headers || {};
  options.credentials = "include";
  options.headers["X-CSRF-TOKEN"] = getCookie("csrf_access_token");

  const res = await fetch(path, options);
  const json = await res.json();
  // 不抛异常，让调用方根据 code 决定
  return json;
}

const api = localApiFetch;

/* UI helpers */
function showSuccess(msg) {
    clearContainer();
    insertContainer('info', msg);

}

function showErrorMsg(msg) {
  clearContainer();
    insertContainer('danger', msg);

}

function showFieldErrors(errors) {
  showErrors(errors, 1);
}

/* 填充表单 */
async function loadProfile() {
  try {
    const res = await api('/api/account/profile', { method: 'GET' });
    if (res.code !== 200 && res.code !== 201) {
      showErrorMsg('无法获取用户信息');
      return;
    }
    const data = res.data || {};

    document.getElementById('username').value = data.username || '';
    document.getElementById('gender').value = data.gender || '';
    document.getElementById('age').value = data.age || '';
    document.getElementById('bio').value = data.bio || '';
    document.getElementById('avatar_url').value = data.avatar_url || '';
    const preview = document.getElementById('avatar-preview');
        if (data.avatar_url) {
          preview.src = data.avatar_url;
        } else {
          preview.src = "https://userpic.codeforces.org/no-title.jpg";
        }

  } catch (e) {
    console.error(e);
    showErrorMsg('读取用户信息失败');
  }
}

/* 头像 URL 改变时预览 */
document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatar_url');
  const preview = document.getElementById('avatar-preview');

  avatarInput.addEventListener('input', () => {
    const url = avatarInput.value.trim();
    if (!url) {
      // 恢复默认图（如果你有 default-avatar）
      preview.src = "https://userpic.codeforces.org/no-title.jpg";
      return;
    }
    // 试图加载图片，加载失败则不改变 src
    const img = new Image();
    img.onload = () => preview.src = url;
    img.onerror = () => {/* ignore on error */};
    img.src = url;
  });

  // 取消按钮行为：回到 profile 页面或刷新
  document.getElementById('cancel-btn').addEventListener('click', (e) => {
    e.preventDefault();
    // 你可以改成跳转到其它页面
    window.location.href = "/account/profile";
  });

  // 表单提交
  document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // 简单前端校验
    const username = document.getElementById('username').value.trim();
    if (!username) {
      document.getElementById('username').classList.add('is-invalid');
      return;
    } else {
      document.getElementById('username').classList.remove('is-invalid');
    }

    const payload = {
      username: username
    };
    const gender = document.getElementById('gender').value;
    if (gender) payload.gender = gender;

    const ageVal = document.getElementById('age').value;
    if (ageVal !== '') {
      const age = Number(ageVal);
      if (!Number.isInteger(age) || age < 0 || age > 200) {
        showErrorMsg('年龄必须为 0-200 之间的整数');
        return;
      }
      payload.age = age;
    }

    const bio = document.getElementById('bio').value.trim();
    if (bio) payload.bio = bio;

    const avatar = document.getElementById('avatar_url').value.trim();
    if (avatar) payload.avatar_url = avatar;

    // 发送请求
    try {
      const res = await api('/api/account/profile/change', {
        method: 'PUT',
        headers: {
            'Content-Type':'application/json',
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        },
        body: JSON.stringify(payload)
      });
      console.log(res);
      if (res.code === 200 || res.code === 201) {
        showSuccess('个人资料已更新');
        // 如果后端返回 data，可能包含 username 等最新信息
        // 你可以选择刷新页面或更新 navbar
        // 例如：window.location.reload();
      } else if (res.code === 400 && res.errors) {
        showFieldErrors(res.errors);
      } else {
        showErrorMsg(res.message || '更新失败');
      }
    } catch (err) {
      console.error(err);
      showErrorMsg('网络或服务器错误');
    }
  });

  // 页面加载完再拉数据
  loadProfile();
});