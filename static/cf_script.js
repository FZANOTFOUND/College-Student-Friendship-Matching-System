// static/cf_script.js
// 方案 B：等待头像（titlePhoto）准备好再 append 卡片
// 兼容后端返回 { data: {...} } 或 { username: {...} } 两种形式
// 使用：输入框可用逗号或空格分隔多个 handle

(() => {
  // 占位图（data URI），避免 img.src 为空
  const AVATAR_FALLBACK_DATAURI = 'data:image/svg+xml;utf8,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72">' +
    '<rect width="100%" height="100%" fill="#eee"/>' +
    '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#999" font-size="10">no avatar</text>' +
    '</svg>'
  );

  // DOM
  const input = document.getElementById('handleInput');
  const btn = document.getElementById('fetchBtn');
  const resultsContainer = document.getElementById('resultsContainer');
  const okCountEl = document.getElementById('okCount');
  const waCountEl = document.getElementById('waCount');
  const statusMsg = document.getElementById('statusMsg');

  // helpers
  const safeNum = x => { const n = Number(x); return Number.isFinite(n) ? n : 0; };
  const titleCase = s => (s||'').toString().split(/\s+/).map(w => w ? (w[0].toUpperCase()+w.slice(1)) : w).join(' ');

  // 根据 rating 返回颜色类（并可直接 add 到元素上）
  function getColorClassByRating(rating) {
    rating = safeNum(rating);
    if (rating >= 4000) return 'user-4000';
    if (rating >= 3000) return 'user-legendary';
    if (rating >= 2400) return 'user-red';
    if (rating >= 2100) return 'user-orange';
    if (rating >= 1900) return 'user-violet';
    if (rating >= 1600) return 'user-blue';
    if (rating >= 1400) return 'user-cyan';
    if (rating >= 1200) return 'user-green';
    if (rating > 0) return 'user-gray';
    return 'user-black';
  }

  // 使用 CF 官方 API 获取 titlePhoto（备用）
  async function fetchTitlePhotoFromCFApi(handle) {
    try {
      const r = await fetch(`https://codeforces.com/api/user.info?handles=${encodeURIComponent(handle)}`);
      if (!r.ok) return null;
      const j = await r.json();
      if (j && j.status === 'OK' && Array.isArray(j.result) && j.result.length > 0) {
        // API 返回可能包含 avatar 或 titlePhoto
        return j.result[0].titlePhoto || j.result[0].avatar || null;
      }
    } catch (e) {
      // ignore
    }
    return null;
  }

  // 将 display name 塞入元素：当 rating >=3000 时首字母单独 span
  function fillDisplayName(el, username, rating) {
    el.innerHTML = '';
    const uname = (username || '');
    if (safeNum(rating) >= 3000 && uname.length > 0) {
      const first = document.createElement('span');
      first.className = safeNum(rating) >= 4000 ? 'user-4000-first-letter' : 'legendary-user-first-letter';
      first.textContent = uname[0];
      el.appendChild(first);
      el.appendChild(document.createTextNode(uname.slice(1)));
    } else {
      el.textContent = uname;
    }
  }

  // 构造并返回卡片 DOM（不 append）
  function buildCardDOM({ username, info, avatarUrl }) {
    // card
    const card = document.createElement('article');
    card.className = 'user-card';
    card.setAttribute('data-cache', info.cache ? 'true' : 'false');
    card.setAttribute('data-status', info.status || '');
    console.log(info);
    // left: avatar
    const left = document.createElement('div');
    left.className = 'card-left';
    const img = document.createElement('img');
    img.className = 'card-avatar';
    img.alt = `${username} avatar`;
    img.src = avatarUrl || AVATAR_FALLBACK_DATAURI;
    left.appendChild(img);

    // right
    const right = document.createElement('div');
    right.className = 'card-right';

    const rankTitle = document.createElement('div');
    rankTitle.className = 'rank-title';
    rankTitle.textContent = titleCase(info.rank || '');

    const displayName = document.createElement('div');
    displayName.className = 'display-name';
    fillDisplayName(displayName, info.handle, info.rating);

    // rating line
    const ratingLine = document.createElement('div');
    ratingLine.className = 'rating-line';
    const iconWrap = document.createElement('span');
    iconWrap.className = 'rating-icon';
    iconWrap.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#3ea1ff" d="M12 2L15 8l6 .9-4.5 4 1.2 6L12 17l-5.7 2.9L7.5 13 3 9l6-.9z"/></svg>';
    const label = document.createElement('span');
    label.className = 'rating-label';
    label.textContent = '等级分:';
    const value = document.createElement('span');
    value.className = 'rating-value';
    value.textContent = (info.rating !== undefined && info.rating !== null) ? info.rating : '';
    const maxinfo = document.createElement('span');
    maxinfo.className = "max-info"
    maxinfo.appendChild(document.createTextNode("(max."))
    const t = document.createElement('span');
    t.className = getColorClassByRating(info.maxrating)
    t.classList.add('bold');
    t.textContent = `${info.maxrating}, ${info.maxrank}`
    maxinfo.appendChild(t)
    maxinfo.appendChild(document.createTextNode(")"))
    ratingLine.appendChild(iconWrap);
    ratingLine.appendChild(label);
    ratingLine.appendChild(value);
    ratingLine.appendChild(maxinfo);

    // apply color classes
    const colorClass = getColorClassByRating(info.rating);
    displayName.classList.add(colorClass);
    value.classList.add(colorClass);
    // apply also to rankTitle for visual consistency
    rankTitle.classList.add(colorClass);

    right.appendChild(rankTitle);
    right.appendChild(displayName);
    right.appendChild(ratingLine);

    card.appendChild(left);
    card.appendChild(right);
    return card;
  }

  // 主流程：按 handle 列表顺序查询，等待 avatar/titlePhoto 后 append
  async function queryHandles() {
    // console.log(1111111);
    let text = input.value || '';
    text = text.trim();
    if (!text) return;

    // split by comma or whitespace
    const handles = text.split(/[, \t\n]+/).map(s => s.trim()).filter(Boolean);
    resultsContainer.innerHTML = ''; // 清空旧结果
    console.log(handles)
    let ok = 0, wa = 0;
    statusMsg.textContent = '查询中...';
    okCountEl.textContent = 0;
    waCountEl.textContent = 0;
    for (const raw of handles) {
      const handle = raw;
      try {
        // 请求后端接口
        console.log(`/api/codeforces/single?handle=${encodeURIComponent(handle)}`);
        const resp = await fetch(`/api/codeforces/single?handle=${encodeURIComponent(handle)}`);
        if (!resp.ok) {
          wa++;
          // show small error card
          const err = document.createElement('div');
          err.className = 'user-card error';
          err.textContent = `${handle} — 网络错误 (${resp.status})`;
          resultsContainer.appendChild(err);
          continue;
        }
        const json = await resp.json();

        // 兼容两种后端返回结构
        let info = null;
        let username = handle;
        if (json && json.data && typeof json.data === 'object') {
          info = json.data;
          username = info.handle || handle;
        } else {
          const e = Object.entries(json || {})[0];
          if (e) { username = e[0]; info = e[1]; } else { info = {}; }
        }

        // 状态检查
        if ((info.status || '').toString().toLowerCase() !== 'ok') {
          wa++;
          const err = document.createElement('div');
          err.className = 'user-card error';
          err.textContent = `${username} — Error: ${info.msg || 'unknown'}`;
          resultsContainer.appendChild(err);
          continue;
        }

        ok++;

        // 方案 B：确认 avatar/titlePhoto URL（优先使用 info.titlePhoto）
        let avatarUrl = null;
        if (info.titlePhoto) avatarUrl = info.titlePhoto;
        else if (info.avatar) avatarUrl = info.avatar;
        else {
          // fallback to official API user.info
          const apiPhoto = await fetchTitlePhotoFromCFApi(username);
          avatarUrl = apiPhoto || null;
        }
        if (!avatarUrl) avatarUrl = AVATAR_FALLBACK_DATAURI;

        // 构造 DOM 并 append
        const card = buildCardDOM({ username, info, avatarUrl });
        resultsContainer.appendChild(card);

      } catch (err) {
        wa++;
        const errCard = document.createElement('div');
        errCard.className = 'user-card error';
        errCard.textContent = `${handle} — 异常: ${err && err.message ? err.message : String(err)}`;
        resultsContainer.appendChild(errCard);
        console.error(err);
      } finally {
        okCountEl.textContent = ok;
        waCountEl.textContent = wa;
      }
    } // end for

    statusMsg.textContent = ok === 0 ? (wa > 0 ? '没有成功的返回（查看控制台）' : '没有查询到数据') : `查询完成：${ok} 个 OK，${wa} 个错误`;
  }

  // event
  btn.addEventListener('click', queryHandles);
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); queryHandles(); } });

})();
