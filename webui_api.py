import streamlit as st
from datetime import datetime
import requests # 导入requests库

st.set_page_config(page_title="六爻排盘", layout="wide")

# --- 核心辅助函数，用于生成精美的卦象HTML (这部分无需修改) ---
def display_hexagram_visual(hex_data: dict, moving_line: int = None):
    """
    使用HTML和CSS动态生成一个精美的、对齐的卦象表格
    """
    # ... (这整个函数的内容和您提供的版本完全一样，为了简洁省略)
    # 定义动爻符号
    moving_indicators = {
        '0': 'O',  # 阳动之符
        '1': 'X'   # 阴动之符
    }

    st.subheader(hex_data['name'])
    st.caption(f"上卦：{hex_data['upper_trigram']} | 下卦：{hex_data['lower_trigram']}")

    html_parts = ["<table style='width: 100%; border-collapse: collapse; font-family: \"KaiTi\", \"STKaiti\", \"楷体\", serif;'>"]
    
    for i in range(6):
        yao_position = 6 - i
        yao_binary_char = hex_data['yao_binary'][i]
        
        # 1. 使用HTML和CSS来绘制爻象
        if yao_binary_char == '0':  # 阳爻
            line_symbol = '<div style="width: 90px; height: 16px; background-color: #3c4043; margin: auto; border-radius: 3px;"></div>'
        else:  # 阴爻
            line_symbol = (
                '<div style="width: 90px; height: 16px; margin: auto; display: flex; justify-content: space-between;">'
                '<div style="width: 38px; height: 100%; background-color: #3c4043; border-radius: 3px;"></div>'
                '<div style="width: 38px; height: 100%; background-color: #3c4043; border-radius: 3px;"></div>'
                '</div>'
            )

        # 2. 动爻标志 (O/X)
        indicator_text = "&nbsp;"
        if moving_line and yao_position == moving_line:
            indicator_char = moving_indicators[yao_binary_char]
            indicator_text = f"<span style='color: #FF4B4B; font-weight: bold; font-size: 20px;'>{indicator_char}</span>"

        # 3. 纳甲六亲 和 4. 世应标志
        main_details = "&nbsp;"
        shi_ying_marker = "&nbsp;"
        if hex_data['liuyao'] and len(hex_data['liuyao']) == 6:
            raw_details_text = hex_data['liuyao'][i]['name']
            if raw_details_text.endswith(" 世"):
                main_details = raw_details_text[:-2].strip()
                shi_ying_marker = "世"
            elif raw_details_text.endswith(" 应"):
                main_details = raw_details_text[:-2].strip()
                shi_ying_marker = "应"
            else:
                main_details = raw_details_text

        row_html = (
            '<tr style="height: 42px; line-height: 42px;">'
            f'<td style="width: 50%; text-align: right; padding-right: 15px; font-size: 16px;">{main_details}</td>'
            f'<td style="width: 100px; text-align: center;">{line_symbol}</td>'
            f'<td style="width: 40px; text-align: right; padding-right: 15px;">{indicator_text}</td>'
            f'<td style="text-align: left; color: #AAAAAA; font-size: 16px;">{shi_ying_marker}</td>'
            '</tr>'
        )
        html_parts.append(row_html)
    
    html_parts.append("</table>")

    final_html = "".join(html_parts)
    st.markdown(final_html, unsafe_allow_html=True)


# --- Streamlit UI 主体 ---
st.title("☯️ 专业六爻排盘")
st.caption("一个基于时间起卦的六爻排盘工具")
st.divider()

with st.container():
    use_current_time = st.checkbox("使用当前时间进行排盘", value=True)
    target_datetime = None

    if not use_current_time:
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input("选择日期", datetime.now())
        with col2:
            t = st.time_input("选择时间", datetime.now().time())
        target_datetime = datetime.combine(d, t)
    else:
        target_datetime = datetime.now()
        st.info(f"当前起卦时间: {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

# --- 主要修改部分：排盘按钮的逻辑 ---
if st.button("开始排盘", type="primary", use_container_width=True):
    
    # 从secrets中读取API配置
    api_url = st.secrets["API_ENDPOINT"]
    api_key = st.secrets["API_KEY"]

    # 准备API请求的头部和载荷
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    payload = {
        "target_time": target_datetime.isoformat() if target_datetime else None
    }
    
    # 发送API请求并处理响应
    try:
        with st.spinner("正在向API请求排盘结果..."):
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)

        # 检查API响应状态
        if response.status_code == 200:
            result = response.json()
            
            # --- 以下的显示逻辑与之前完全相同 ---
            st.divider()
            st.header("排盘结果")

            with st.expander("详细时间信息"):
                time_info = result['query_time']
                st.write(f"**公历时间**: {time_info['gregorian']}")
                st.write(f"**农历时间**: {time_info['lunar']}")
                ganzhi = time_info['ganzhi']
                st.write("**四柱干支**: ")
                st.code(f"年柱: {ganzhi['year_gz']}\n月柱: {ganzhi['month_gz']}\n日柱: {ganzhi['day_gz']}\n时柱: {ganzhi['hour_gz']}")

            hex_info = result['hexagram']
            col_ben, col_bian = st.columns(2)

            with col_ben:
                with st.container(border=True):
                    st.header("本卦")
                    display_hexagram_visual(hex_info['original'], hex_info['moving_line'])

            with col_bian:
                with st.container(border=True):
                    st.header("变卦")
                    display_hexagram_visual(hex_info['changed'])
        else:
            # 如果API返回错误，则显示错误信息
            st.error(f"API调用失败，状态码: {response.status_code}")
            st.json(response.json())

    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败，请检查API服务是否已启动并且地址正确。")
        st.error(f"错误详情: {e}")