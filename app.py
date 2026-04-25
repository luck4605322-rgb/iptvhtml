import streamlit as st
import requests
import time
from collections import defaultdict

# ==================== 请在这里完整粘贴你的 LANGUAGES 字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.5",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.5 支持界面多语言切换 • 仅第一个成功服务器检测直播/电影/语言分类",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "only_first": "   → 只对第一个成功登录的服务器检测直播数量、电影数量和多国语言分类\n\n",
        "single": "   → 将检测直播数量、电影数量和常用多国语言分类\n\n",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | 直播: {3}个 | 电影: {4}个{5}",
        "no_resource": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | （资源&语言已检测过其他服务器）",
        "lang_stats": " | 语言分类: {0}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.5",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "start_btn": "🚀 Start Batch Test",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        # ... 请把你原来的 English 等其他语言完整复制进来
    }
    # 把你原来的 "Español", "Français" 等也完整粘贴在这里
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# ==================== 你的辅助函数（完整复制） ====================
# 把下面这些函数从你原来的 Python 文件完整复制过来：
# get_language_stats, get_resource_counts, get_language_categories, test_single_server

def get_language_stats(categories):
    # ... 你的原函数
    pass

def get_resource_counts(session, base_url):
    # ... 你的原函数
    pass

def get_language_categories(session, base_url):
    # ... 你的原函数
    pass

def test_single_server(server, username, password, output_placeholder, trans, check_resources=True):
    if not server.startswith("http"):
        server = "http://" + server
    server = server.rstrip("/")
    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    start_time = time.time()
    session = requests.Session()
    
    try:
        resp = session.get(base_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - start_time, 2)
        
        if resp.status_code != 200:
            result = trans.get("http_error", "HTTP Error").format(resp.status_code, elapsed)
            output_placeholder.write(f"{server}  →  {result}\n")
            return result, False
        
        data = resp.json()
        if not (isinstance(data, dict) and "user_info" in data):
            result = trans.get("no_userinfo", "Login failed").format(elapsed)
            output_placeholder.write(f"{server}  →  {result}\n")
            return result, False
        
        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
        
        lang_info = ""
        if check_resources:
            live_c, vod_c = get_resource_counts(session, base_url)
            lang_stats = get_language_categories(session, base_url)
            if lang_stats:
                parts = [f"{k}({v})" for k, v in sorted(lang_stats.items(), key=lambda x: -x[1])]
                lang_info = trans.get("lang_stats", "").format(", ".join(parts[:8]))
            result = trans.get("available", "Available").format(elapsed, status, exp, live_c, vod_c, lang_info)
        else:
            result = trans.get("no_resource", "Available (resources checked elsewhere)").format(elapsed, status, exp)
        
        output_placeholder.write(f"{server}  →  {result}\n")
        return result, True
        
    except Exception as e:
        result = trans.get("unknown", "Unknown error").format(str(e)[:80])
        output_placeholder.write(f"{server}  →  {result}\n")
        return result, False

# ==================== Streamlit 主界面 ====================
def main():
    st.set_page_config(page_title="IPTV 检测工具", layout="centered")
    
    # 语言选择（放在侧边栏，防止加载时出错）
    lang = st.sidebar.selectbox("界面语言 / Language", options=list(LANGUAGES.keys()), index=0)
    trans = LANGUAGES.get(lang, LANGUAGES["简体中文"])   # 容错处理
    
    st.title(trans.get("title", "IPTVNator 批量检测工具 v1.5"))
    
    st.markdown("**检测使用您当前的网络（手机/电脑本地网络）**")

    username = st.text_input(trans.get("username", "用户名:"), "")
    password = st.text_input(trans.get("password", "密码:"), "", type="password")
    
    servers_text = st.text_area(
        trans.get("servers", "服务器地址（一行一个）:"), 
        height=180,
        placeholder="http://example.com:8080\nhttp://test.tv:12345"
    )

    if st.button(trans.get("start_btn", "🚀 开始批量检测"), type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans.get("warning", "请填写完整信息！"))
            return
        
        result_container = st.empty()
        result_container.info(trans.get("running", "").format(len(servers)))
        
        output_placeholder = st.empty()
        
        def run_tests():
            resource_checked = False
            for i, server in enumerate(servers, 1):
                output_placeholder.write(trans.get("detecting", "").format(i, len(servers), server))
                check_res = (not resource_checked) and (i == 1 or len(servers) == 1)
                _, success = test_single_server(server, username, password, output_placeholder, trans, check_res)
                if success and not resource_checked:
                    resource_checked = True
                time.sleep(0.4)
            st.success(trans.get("complete", "").format(len(servers)))
        
        threading.Thread(target=run_tests, daemon=True).start()

    st.caption(trans.get("footer", "Powered by Streamlit"))

if __name__ == "__main__":
    main()
