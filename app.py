import streamlit as st
import requests
import time

st.set_page_config(page_title="IPTV 检测工具", layout="centered")

st.title("IPTVNator 批量检测工具 v2.1 - 极简版")

st.markdown("**检测使用您当前的本地网络**")

username = st.text_input("用户名:", "")
password = st.text_input("密码:", "", type="password")
servers_text = st.text_area("服务器地址（一行一个）:", height=200, 
                            placeholder="rapide-leon.online\nsmart.lionsmart.cc\nlion-star25.com")

if st.button("🚀 开始批量检测", type="primary"):
    servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
    
    if not servers or not username or not password:
        st.error("请填写服务器列表、账号和密码！")
        st.stop()

    total = len(servers)
    st.info(f"🚀 开始检测 {total} 个服务器...")

    progress_bar = st.progress(0)
    output_area = st.empty()
    results = []
    success = 0

    for i, server in enumerate(servers, 1):
        progress_bar.progress(int(i / total * 100))
        output_area.write(f"[{i}/{total}] 检测中: {server}")

        # 简单检测
        try:
            if not server.startswith("http"):
                server = "http://" + server
            url = f"{server.rstrip('/')}/player_api.php?username={username}&password={password}"
            r = requests.get(url, timeout=12)
            if r.status_code == 200 and "user_info" in r.json():
                result = "✅ 可用"
                success += 1
            else:
                result = f"❌ 失败 (HTTP {r.status_code})"
        except Exception as e:
            result = f"❌ 错误: {str(e)[:50]}"

        results.append(f"{server}  →  {result}")
        output_area.write("\n".join(results))
        time.sleep(0.3)

    progress_bar.progress(100)
    st.success(f"✅ 检测完成！成功 {success}/{total} 个")

st.caption("极简稳定版 - 如果还是崩溃，请查看 Manage app → Logs")
