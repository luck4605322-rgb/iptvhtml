import streamlit as st
import requests
import time
from collections import defaultdict
import threading

# ==================== 多国语言字典（保持原样） ====================
LANGUAGES = {
    "简体中文": { ... },   # 请把你原来的 LANGUAGES 字典完整复制到这里
    "English": { ... },
    "Español": { ... },
    "Français": { ... },
    # ... 其他语言保持不变
}

# 请求头（保持原样）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

# ==================== 原有辅助函数（基本保持不变） ====================
# get_language_stats、get_resource_counts、get_language_categories、test_single_server 函数
# 请把你原来的这几个函数完整复制过来（只改 test_single_server 的 result 输出方式）

def test_single_server(server, username, password, placeholder, trans, check_resources=True):
    # ... 保持你原来的逻辑
    # 在成功/失败时，用 placeholder.write(...) 或 st.write 替换原来的 result_text.insert
    # 示例：
    # placeholder.write(f"{server}  →  {result}\n")
    pass   # ← 这里替换成你原来的 test_single_server 内容，改成用 placeholder

# ==================== 主界面 ====================
def main():
    st.set_page_config(page_title="IPTVNator 批量检测", layout="wide")
    
    # 语言选择
    lang = st.sidebar.selectbox("界面语言 / Language", list(LANGUAGES.keys()), index=0)
    trans = LANGUAGES[lang]
    
    st.title(trans["title"])
    st.markdown("**使用您的当前网络进行真实检测**（手机/电脑本地网络）")

    # 输入区域
    username = st.text_input(trans["username"], value="")
    password = st.text_input(trans["password"], value="", type="password")
    
    servers_text = st.text_area(trans["servers"], height=200, 
                                placeholder="http://example.com:8080\nhttp://test.tv:12345\n一行一个")

    if st.button(trans["start_btn"], type="primary"):
        servers = [s.strip() for s in servers_text.strip().splitlines() if s.strip()]
        
        if not servers or not username or not password:
            st.error(trans["warning"])
            return
        
        # 清空并显示开始信息
        result_container = st.empty()
        result_container.write(trans["running"].format(len(servers)))
        
        if len(servers) > 1:
            result_container.write(trans["only_first"])
        else:
            result_container.write(trans["single"])
        
        # 实时输出占位符
        output_placeholder = st.empty()
        
        def run_tests():
            resource_checked = False
            for i, server in enumerate(servers, 1):
                output_placeholder.write(trans["detecting"].format(i, len(servers), server))
                
                check_res = (not resource_checked) and (i == 1 or len(servers) == 1)
                _, success = test_single_server(server, username, password, output_placeholder, trans, check_res)
                
                if success and not resource_checked:
                    resource_checked = True
                time.sleep(0.3)
            
            st.success(trans["complete"].format(len(servers)))
        
        # 在线程中运行（避免阻塞界面）
        thread = threading.Thread(target=run_tests, daemon=True)
        thread.start()

    st.caption(trans["footer"])

if __name__ == "__main__":
    main()
