document.addEventListener('DOMContentLoaded', function () {
    const btnHome = document.getElementById('btn-home');
    const btnReload = document.getElementById('btn-reload');


    if (btnHome) btnHome.addEventListener('click', () => { location.href = '/'; });
    if (btnReload) btnReload.addEventListener('click', () => { location.reload(); });


    // 按 R 刷新, H 回首页
    document.addEventListener('keydown', (e) => {
        if (e.key === 'r' || e.key === 'R') location.reload();
        if (e.key === 'h' || e.key === 'H') location.href = '/';
    });
});