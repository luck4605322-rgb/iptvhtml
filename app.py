import streamlit as st
import requests
import time
import threading

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.6",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "only_first": "   → 仅检测服务器是否可用（简化模式）\n\n",
        "single": "   → 检测服务器是否可用\n\n",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}",
        "unavailable": "❌ 不可用 | 耗时 {0}s"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.6",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "start_btn": "🚀 Start Batch Test",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "only_first": "   → Only checking if server is available (simplified)\n\n",
        "single": "   → Checking if server is available\n\n",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}",
        "unavailable": "❌ Unavailable | Time {0}s"
    }
    # 可继续添加其他语言
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

# ==================== 简化后的单个服务器检测函数 ====================
def test_single_server(server, username, password, output_placeholder, trans):
    if not server or not username or not password:
        output_placeholder.write("❌ 跳过无效输入\n")
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

        # 只提取状态和过期时间
        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            try:
                exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
            except:
                exp = "永久"

        result = trans.get("available", "").format(elapsed, status, exp)
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

    st.title(trans.get("title", "IPTVNator 批量检测工具 v1.6"))
    st.markdown("**检测使用您当前的网络（手机/电脑本地网络）**")

    username = st.text_input(trans.get("username", "用户名:"), "")
    password = st.text_input(trans.get("password", "密码:"), "", type="password")
    
    servers_text = st.text_area(
        trans.get("servers", "服务器地址（一行一个）:"), 
        height=220,
        placeholder="rapide-leon.online\nsmart.lionsmart.cc\nlion-star25.com\n一行一个"
    )

    if st.button(trans.get("start_btn", "🚀 开始批量检测"), type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans.get("warning", "请填写完整信息！"))
            return

        total = len(servers)
        st.info(trans.get("running", "").format(total))
        
        if total > 1:
            st.info(trans.get("only_first", ""))
        else:
            st.info(trans.get("single", ""))

        # 进度条
        progress_bar = st.progress(0)
        output_placeholder = st.empty()

        def run_tests():
            success_count = 0
            for i, server in enumerate(servers, 1):
                # 更新进度条
                progress = int((i / total) * 100)
                progress_bar.progress(progress)
                
                output_placeholder.write(trans.get("detecting", "").format(i, total, server))
                
                _, success = test_single_server(server, username, password, output_placeholder, trans)
                if success:
                    success_count += 1
                
                time.sleep(0.4)  # 防止请求过快

            progress_bar.progress(100)
            st.success(f"{trans.get('complete', '')} 成功: {success_count}/{total}")

        # 启动后台线程
        threading.Thread(target=run_tests, daemon=True).start()

    st.caption("v1.6 简化版 • 只检测是否可用 + 进度条 • 使用本地网络检测")

if __name__ == "__main__":
    main()
