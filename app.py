import streamlit as st
import requests
import time

# ==================== 多国语言（简体中文为主） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.1",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "start_btn": "🚀 开始批量检测",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 检测完成！共检测 {0} 个，成功 {1} 个",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败 | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败",
        "unknown": "❌ 未知错误",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def test_single_server(server, username, password):
    if not server.startswith(("http://", "https://")):
        server = "http://" + server
    server = server.rstrip("/")

    base_url = f"{server}/player_api.php?username={username}&password={password}"
    start_time = time.time()

    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - start_time, 2)

        if resp.status_code != 200:
            return f"❌ HTTP错误 {resp.status_code} | 耗时 {elapsed}s", False

        data = resp.json()
        if not (isinstance(data, dict) and "user_info" in data):
            return f"❌ 登录失败 | 耗时 {elapsed}s", False

        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            try:
                exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
            except:
                exp = "永久"

        return f"✅ 可用 | 耗时 {elapsed}s | 状态: {status} | 过期: {exp}", True

    except requests.exceptions.Timeout:
        return "❌ 超时 (>15s)", False
    except requests.exceptions.ConnectionError:
        return "❌ 连接失败", False
    except Exception as e:
        return f"❌ 错误: {str(e)[:80]}", False

def main():
    st.set_page_config(page_title="IPTV 检测工具", layout="centered")
    trans = LANGUAGES["简体中文"]

    st.title(trans["title"])
    st.markdown("**检测使用您当前的本地网络**")

    username = st.text_input(trans["username"], "")
    password = st.text_input(trans["password"], "", type="password")
    servers_text = st.text_area(trans["servers"], height=200, placeholder="rapide-leon.online\nsmart.lionsmart.cc")

    if st.button(trans["start_btn"], type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans["warning"])
            st.stop()

        total = len(servers)
        st.info(trans["running"].format(total))

        progress_bar = st.progress(0)
        output_area = st.empty()
        results = []
        success_count = 0

        for i, server in enumerate(servers, 1):
            progress_bar.progress(int(i / total * 100))
            output_area.write(f"[{i}/{total}] 检测中: {server}")

            result, success = test_single_server(server, username, password)
            if success:
                success_count += 1
            results.append(f"{server}  →  {result}")
            output_area.write("\n".join(results))

            time.sleep(0.3)

        progress_bar.progress(100)
        st.success(trans["complete"].format(total, success_count))

    st.caption("v2.1 极简稳定版 • 一行一个结果")

if __name__ == "__main__":
    main()
