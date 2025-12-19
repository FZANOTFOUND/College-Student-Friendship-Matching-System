// static/js/tags.js

function translateCategory(category) {
    const map = {
        interest: "兴趣",
        tech: "技术",
        purpose: "目的",
        profile: "用户特征"
    };

    return map[category] || "其他";
}

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("tags-container");
  if (!container) return;

  // 可选：如果你的后端有 CSRF 保护，需要把 CSRF token 放到 meta 标签然后读取
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  // fetch helper


  // 加载所有 tags 和用户已有 tags
  async function loadTags() {
    container.innerHTML = `<div class="text-muted">加载中…</div>`;
    try {
      const [allResp, userResp] = await Promise.all([
        apiFetch("/api/tags/all"),
        apiFetch("/api/tags/user")
      ]);
      const tagsByCategory = allResp.data || {};
      const userTagIds = new Set(userResp.data || []);
      console.log(userTagIds);
      console.log(tagsByCategory);
      renderTags(tagsByCategory, userTagIds);
    } catch (err) {
      console.error("加载标签失败", err);
      container.innerHTML = `<div class="alert alert-danger">加载标签失败，请刷新重试</div>`;
    }
  }

  function renderTags(tagsByCategory, userTagIds) {
    const wrapper = document.createElement("div");

    for (const [category, tags] of Object.entries(tagsByCategory)) {
      const card = document.createElement("div");
      card.className = "card mb-3";
      const head = document.createElement("div");
      head.className = "card-header";
      head.textContent = translateCategory(category);
      const body = document.createElement("div");
      body.className = "card-body";

      const row = document.createElement("div");
      row.className = "row";

      tags.forEach(t => {
        const col = document.createElement("div");
        col.className = "col-md-4 mb-2";

        const id = `tag-checkbox-${t.tag_id}`;
        const div = document.createElement("div");
        div.className = "form-check";

        const input = document.createElement("input");
        input.className = "form-check-input";
        input.type = "checkbox";
        input.id = id;
        input.dataset.tagId = t.tag_id;
        input.checked = userTagIds.has(t.tag_id);

        // label
        const label = document.createElement("label");
        label.className = "form-check-label";
        label.htmlFor = id;
        label.innerHTML = `<strong>${t.tag_name}</strong><br/><small class="text-muted">${t.description || ""}</small>`;

        // attach change listener
        input.addEventListener("change", (ev) => handleToggle(ev.target));

        div.appendChild(input);
        div.appendChild(label);
        col.appendChild(div);
        row.appendChild(col);
      });

      body.appendChild(row);
      card.appendChild(head);
      card.appendChild(body);
      wrapper.appendChild(card);
    }

    container.innerHTML = "";
    container.appendChild(wrapper);
  }

  // 当 checkbox 切换时
  async function handleToggle(inputEl) {
    const tagId = parseInt(inputEl.dataset.tagId, 10);
    const checked = inputEl.checked;

    // 简单的 UI 锁 / 禁用
    inputEl.disabled = true;

    try {
      if (checked) {
        // PUT 添加
        await apiFetch("/api/tags/change", {
          method: "PUT",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({tag_id: tagId})
        });
        showToast("已添加标签");
      } else {
        // DELETE 删除
        await apiFetch("/api/tags/change", {
          method: "DELETE",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({tag_id: tagId})
        });
        showToast("已移除标签");
      }
    } catch (err) {
      console.error("更新标签失败", err);
      // 回滚 UI 状态
      inputEl.checked = !checked;
      showToast("操作失败，请重试", true);
    } finally {
      inputEl.disabled = false;
    }
  }

  // 简单提示（可以换成 Bootstrap toast）
  function showToast(msg, isError=false) {
    const node = document.createElement("div");
    node.className = `alert ${isError ? "alert-danger" : "alert-success"} toast-message`;
    node.style.position = "fixed";
    node.style.right = "20px";
    node.style.bottom = "20px";
    node.style.zIndex = 1050;
    node.textContent = msg;
    document.body.appendChild(node);
    setTimeout(() => node.classList.add("fade-out"), 2200);
    setTimeout(() => node.remove(), 2800);
  }

  loadTags();
});
