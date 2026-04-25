import streamlit as st
import requests
import time
from collections import defaultdict
import threading

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.5",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
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
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | Live: {3} | Movies: {4}{5}",
        "no_resource": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | (Resources checked on another server)",
        "lang_stats": " | Languages: {0}"
    }
    # 你可以继续在这里添加 Español、Français 等语言
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

# ==================== 语言分类映射 ====================
LANGUAGE_MAP = {
    "english": "English", "eng": "English",
    "arabic": "Arabic", "ara": "Arabic",
    "chinese": "Chinese", "china": "Chinese", "中文": "Chinese",
    "spanish": "Spanish", "esp": "Spanish",
    "french": "French", "fra": "French",
    "german": "German", "deu": "German",
    "italian": "Italian", "ita": "Italian",
    "russian": "Russian", "rus": "Russian",
    "turkish": "Turkish", "tur": "Turkish",
    "portuguese": "Portuguese", "por": "Portuguese",
    "hindi": "Hindi/India", "india": "Hindi/India",
    "korean": "Korean", "kor": "Korean",
    "japanese": "Japanese", "jpn": "Japanese",
}

# ==================== 辅助函数 ====================
def get_language_stats(categories):
    lang_count = defaultdict(int)
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        name = str(cat.get("category_name", "")).lower()
        matched = False
        for key, lang in LANGUAGE_MAP.items():
            if key in name:
                lang_count[lang] += 1
                matched = True
                break
        if not matched and any(w in name for w in ["international", "world", "global", "sport", "news"]):
            lang_count["International"] += 1
    return dict(lang_count)

def get_resource_counts(session, base_url):
    live_count = vod_count = 0
    try:
        r = session.get(f"{base_url}&action=get_live_streams", headers=HEADERS, timeout=12)
        if r.status_code == 200 and isinstance(r.json(), list):
            live_count = len(r.json())
    except:
        pass
    try:
        r = session.get(f"{base_url}&action=get_vod_streams", headers=HEADERS, timeout=12)
        if r.status_code == 200 and isinstance(r.json(), list):
            vod_count = len(r.json())
    except:
        pass
    return live_count, vod_count

def get_language_categories(session, base_url):
    try:
        r = session.get(f"{base_url}&action=get_live_categories", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            cats = r.json()
            if isinstance(cats, list):
                return get_language_stats(cats)
    except:
        pass
    return {}

def test_single_server(server, username, password, output_placeholder, trans, check_resources=True):
    if not server or not username or not password:
        output_placeholder.write("❌ 跳过无效服务器\n")
        return "无效输入", False

    if not server.startswith(("http://", "https://")):
        server = "http://" + server
    server = server.rstrip("/")

    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    start_time = time.time()
    session = requests.Session()
    
    try:
        resp = session.get(base_url, headers=HEADERS, timeout=15, allow_redirects=True)
        elapsed = round(time.time() - start_time, 2)

        if resp.status_code != 200:
            result = trans.get("http_error", "HTTP错误").format(resp.status_code, elapsed)
            output_placeholder.write(f"{server}  →  {result}\n")
            return result, False

        data = resp.json()
        if not (isinstance(data, dict) and "user_info" in data):
            result = trans.get("no_userinfo", "登录失败").format(elapsed)
            output_placeholder.write(f"{server}  →  {result}\n")
            return result, False

        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            try:
                exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
            except:
                exp = "永久"

        lang_info = ""
        live_c = vod_c = 0

        if check_resources:
            live_c, vod_c = get_resource_counts(session, base_url)
            lang_stats = get_language_categories(session, base_url)
            if lang_stats:
                parts = [f"{k}({v})" for k, v in sorted(lang_stats.items(), key=lambda x: -x[1])]
                lang_info = trans.get("lang_stats", "").format(", ".join(parts[:8]))
            result = trans.get("available", "").format(elapsed, status, exp, live_c, vod_c, lang_info)
        else:
            result = trans.get("no_resource", "").format(elapsed, status, exp)

        output_placeholder.write(f"{server}  →  {result}\n")
        return result, True

    except requests.exceptions.Timeout:
        result = trans.get("timeout", "❌ 超时 (>15s)")
    except requests.exceptions.ConnectionError:
        result = trans.get("conn_fail", "❌ 连接失败")
    except Exception as e:
        result = trans.get("unknown", "❌ 未知错误").format(str(e)[:100])

    output_placeholder.write(f"{server}  →  {result}\n")
    return result, False

# ==================== 主界面 ====================
def main():
    st.set_page_config(page_title="IPTVNator 批量检测工具", layout="centered")
    
    # 语言选择
    lang = st.sidebar.selectbox(
        "界面语言 / Language", 
        options=list(LANGUAGES.keys()), 
        index=0
    )
    trans = LANGUAGES.get(lang, LANGUAGES["简体中文"])

    st.title(trans.get("title", "IPTVNator 批量检测工具 v1.5"))
    st.markdown("**检测使用您当前的网络（手机/电脑本地网络）**")

    username = st.text_input(trans.get("username", "用户名:"), "")
    password = st.text_input(trans.get("password", "密码:"), "", type="password")
    
    servers_text = st.text_area(
        trans.get("servers", "服务器地址（一行一个）:"), 
        height=220,
        placeholder="rapide-leon.online\nsmart.lionsmart.cc\n一行一个"
    )

    if st.button(trans.get("start_btn", "🚀 开始批量检测"), type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans.get("warning", "请填写完整信息！"))
            return

        # 显示开始信息
        st.info(trans.get("running", "").format(len(servers)))
        
        if len(servers) > 1:
            st.info(trans.get("only_first", ""))
        else:
            st.info(trans.get("single", ""))

        # 实时输出区域
        output_placeholder = st.empty()

        def run_tests():
            resource_checked = False
            for i, server in enumerate(servers, 1):
                output_placeholder.write(trans.get("detecting", "").format(i, len(servers), server))
                check_res = (not resource_checked) and (i == 1 or len(servers) == 1)
                _, success = test_single_server(server, username, password, output_placeholder, trans, check_res)
                if success and not resource_checked:
                    resource_checked = True
                time.sleep(0.5)
            st.success(trans.get("complete", "").format(len(servers)))

        # 启动线程
        threading.Thread(target=run_tests, daemon=True).start()

    st.caption("v1.5 Streamlit版 • 检测结果反映您本地的网络情况")

if __name__ == "__main__":
    main()
