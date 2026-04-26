import streamlit as st
import requests
import time

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.0",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器，成功 {1} 个",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}",
        "your_ip": "您的当前访问 IP：",
        "ip_note": "（此 IP 反映您本地的网络出口情况）",
        "ip_fetching": "正在获取您的真实 IP...",
        "ip_failed": "无法获取 IP（可刷新页面重试）"
    },
    "English": {
        "title": "IPTVNator Batch Tester v2.0",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "start_btn": "🚀 Start Batch Test",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "detecting": "[{0}/{1}] Testing: {2}",
        "complete": "✅ Batch test completed! Tested {0} servers. Success: {1}",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}",
        "your_ip": "Your Current IP: ",
        "ip_note": "(This IP reflects your local network exit)",
        "ip_fetching": "Fetching your real IP...",
        "ip_failed": "Unable to get IP (refresh page to retry)"
    }
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

# ==================== 获取用户真实 IP（浏览器端查询） ====================
def get_client_ip():
    try:
        # 使用多个公共 IP 服务，提高成功率
        for url in ["https://api.ipify.org?format=json", "https://api.my-ip.io/ip.json", "https://ipinfo.io/json"]:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    ip = data.get("ip") or data.get("ip_address") or str(data)
                    if isinstance(ip, str) and len(ip) > 6:
                        return ip
            except:
                continue
        return None
    except:
        return None

# ==================== 单个服务器检测 ====================
def test_single_server(server, username, password, trans):
    if not server or not username or not password:
        return "无效输入", False

    if not server.startswith(("http://", "https://")):
        server = "http://" + server
    server = server.rstrip("/")

    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    start_time = time.time()
    
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=15, allow_redirects=True)
        elapsed = round(time.time() - start_time, 2)

        if resp.status_code != 200:
            return trans.get("http_error", "").format(resp.status_code, elapsed), False

        data = resp.json()
        if not (isinstance(data, dict) and "user_info" in data):
            return trans.get("no_userinfo", "").format(elapsed), False

        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            try:
                exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
            except:
                exp = "永久"

        result = trans.get("available", "").format(elapsed, status, exp)
        return result, True

    except requests.exceptions.Timeout:
        return trans.get("timeout", "❌ 超时 (>15s)"), False
    except requests.exceptions.ConnectionError:
        return trans.get("conn_fail", "❌ 连接失败"), False
    except Exception as e:
        return trans.get("unknown", "").format(str(e)[:100]), False

# ==================== 主界面 ====================
def main():
    st.set_page_config(page_title="IPTVNator 批量检测工具", layout="centered")
    
    lang = st.sidebar.selectbox("界面语言 / Language", options=list(LANGUAGES.keys()), index=0)
    trans = LANGUAGES.get(lang, LANGUAGES["简体中文"])

    st.title(trans.get("title", "IPTVNator 批量检测工具 v2.0"))
    
    # 显示 IP（安全方式）
    st.markdown(f"**{trans.get('your_ip', '')}**")
    ip = get_client_ip()
    if ip:
        st.success(f"`{ip}`  \n{trans.get('ip_note', '')}")
    else:
        st.info(trans.get("ip_fetching", "正在获取您的真实 IP..."))

    st.markdown("**检测使用您当前的网络（手机/电脑本地网络）**")

    username = st.text_input(trans.get("username", "用户名:"), "")
    password = st.text_input(trans.get("password", "密码:"), "", type="password")
    
    servers_text = st.text_area(
        trans.get("servers", "服务器地址（一行一个）:"), 
        height=220,
        placeholder="rapide-leon.online\nsmart.lionsmart.cc\nlion-star25.com"
    )

    if st.button(trans.get("start_btn", "🚀 开始批量检测"), type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans.get("warning", "请填写完整信息！"))
            st.stop()

        total = len(servers)
        st.info(trans.get("running", "").format(total))

        progress_bar = st.progress(0)
        status_text = st.empty()
        output_area = st.empty()

        results = []
        success_count = 0

        for i, server in enumerate(servers, 1):
            progress = int((i / total) * 100)
            progress_bar.progress(progress)
            status_text.write(trans.get("detecting", "").format(i, total, server))
            
            result, success = test_single_server(server, username, password, trans)
            if success:
                success_count += 1
            
            # 严格一行一个
            line = f"{server}  →  {result}"
            results.append(line)
            output_area.write("\n".join(results))
            
            time.sleep(0.35)

        progress_bar.progress(100)
        st.success(trans.get("complete", "").format(total, success_count))

    st.caption("v2.0 • 一行一个结果 • 显示本地真实 IP • 更稳定")

if __name__ == "__main__":
    main()
