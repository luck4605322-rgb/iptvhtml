import streamlit as st
import requests
import time

st.set_page_config(page_title="IPTV 检测", layout="centered")

st.title("IPTVNator 批量检测工具 - 测试版")

st.write("如果看到这个页面，说明应用已成功启动")

username = st.text_input("用户名:", "")
password = st.text_input("密码:", "", type="password")
servers_text = st.text_area("服务器地址（一行一个）:", height=150)

if st.button("🚀 测试检测"):
    st.info("开始简单测试...")
    servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
    
    for server in servers[:3]:  # 只测试前3个，避免超时
        try:
            if not server.startswith("http"):
                server = "http://" + server
            url = f"{server}/player_api.php?username={username}&password={password}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                st.success(f"{server} → 连接成功 (HTTP 200)")
            else:
                st.error(f"{server} → HTTP {r.status_code}")
        except Exception as e:
            st.error(f"{server} → 错误: {str(e)[:100]}")
        time.sleep(1)

st.caption("这是最简测试版 • 如果这个能打开，我们再逐步加功能")
