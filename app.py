import streamlit as st
import requests
import time

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.9",
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
        "unavailable": "❌ 不可用 | 耗时 {0}s",
        "your_ip": "您的当前访问 IP：",
        "ip_note": "（此 IP 反映您本地的网络出口情况）",
        "ip_unavailable": "无法获取 IP（可能是本地开发或网络问题）"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.9",
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
        "unavailable": "❌ Unavailable | Time {0}s",
        "your_ip": "Your Current IP: ",
        "ip_note": "(This IP reflects your local network exit)",
        "ip_unavailable": "Unable to get IP (local dev or network issue)"
    }
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

# ==================== 获取客户端 IP ====================
def get_client_ip():
    try:
        ip = st.context.ip_address
        if ip:
            return ip
        return "获取中..."
    except:
        return None

# ==================== 单个服务器检测（简化版） ====================
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

    st.title(trans.get("title", "IPTVNator 批量检测工具 v1.9"))
    
    # 显示本地 IP
    ip = get_client_ip()
    if ip:
        st.markdown(f"**{trans.get('your_ip', '')}** `{ip}`  \n{trans.get('ip_note', '')}")
    else:
        st.markdown(f"**{trans.get('your_ip', '')}** {trans.get('ip_unavailable', '')}")
    
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
            st.stop()

        total = len(servers)
        st.info(trans.get("running", "").format(total))

        progress_bar = st.progress(0)
        status_text = st.empty()
        output_area = st.empty()   # 专门用于一行一个结果

        results = []
        success_count = 0

        for i, server in enumerate(servers, 1):
            progress = int((i / total) * 100)
            progress_bar.progress(progress)
            
            status_text.write(trans.get("detecting", "").format(i, total, server))
            
            result, success = test_single_server(server, username, password, trans)
            if success:
                success_count += 1
            
            # 严格一行一个结果
            line = f"{server}  →  {result}"
            results.append(line)
            output_area.write("\n".join(results))
            
            time.sleep(0.35)

        progress_bar.progress(100)
        st.success(trans.get("complete", "").format(total, success_count))

    st.caption("v1.9 • 一行一个结果 • 显示本地 IP • 使用当前网络检测")

if __name__ == "__main__":
    main()
