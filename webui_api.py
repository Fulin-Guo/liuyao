import streamlit as st
from datetime import datetime
import requests # 导入requests库
import argparse
import signal
import sys

# --- 可选：启用 Ctrl+C 终止程序 ---
def _sigint_handler(signum, frame):
    # 在终端打印信息，并优雅退出
    print("检测到 Ctrl+C，正在退出 Streamlit 应用…")
    sys.exit(0)

def _parse_ctrlc_option():
    # 使用 parse_known_args 以兼容 Streamlit 自身参数
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--enable-ctrlc-exit",
        action="store_true",
        help="启用 Ctrl+C 终止程序的选项"
    )
    args, _ = parser.parse_known_args()
    return args.enable_ctrlc_exit

# --- 手工指定爻位转换函数 ---
def convert_manual_yaos_to_hexagram_data(manual_yaos):
    """
    将手工指定的爻位转换为卦象数据格式
    
    Args:
        manual_yaos: 包含6个爻位选择的列表，从初爻到上爻
        
    Returns:
        tuple: (ben_gua_binary, bian_gua_binary, moving_lines)
    """
    # 将爻位选择转换为二进制和动爻信息
    ben_gua_bits = []
    moving_lines = []
    
    for i, yao_choice in enumerate(manual_yaos):
        if "阳爻" in yao_choice:
            ben_gua_bits.append('0')  # 阳爻用0表示
        else:
            ben_gua_bits.append('1')  # 阴爻用1表示
            
        if "动" in yao_choice:
            moving_lines.append(i + 1)  # 记录动爻位置（1-6）
    
    # 构建本卦二进制串（从上爻到初爻的顺序）
    ben_gua_binary = ''.join(reversed(ben_gua_bits))
    
    # 处理动爻
    if len(moving_lines) == 0:
        # 没有动爻，变卦与本卦相同
        bian_gua_binary = ben_gua_binary
    else:
        # 有动爻，所有动爻都变化
        bian_gua_bits = list(ben_gua_binary)
        for ml in moving_lines:
            change_index = 6 - ml  # 转换为字符串索引
            bian_gua_bits[change_index] = str(1 - int(bian_gua_bits[change_index]))
        bian_gua_binary = ''.join(bian_gua_bits)
    
    return ben_gua_binary, bian_gua_binary, moving_lines

def create_manual_hexagram_result(manual_yaos):
    """
    根据手工指定的爻位创建卦象结果
    """
    # 转换手工指定的爻位为卦象数据
    ben_gua_binary, bian_gua_binary, moving_lines = convert_manual_yaos_to_hexagram_data(manual_yaos)
    
    try:
        # 读取API配置
        api_url = st.secrets["API_ENDPOINT"]
        api_key = st.secrets["API_KEY"]
        
        # 使用当前时间调用API，然后替换卦象数据
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "target_time": datetime.now().isoformat()
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            # 获取API响应作为模板
            api_result = response.json()
            
            # 替换卦象数据为手工指定的内容
            # 需要重新解析二进制串为完整的卦象信息
            
            # 建立二进制 -> 卦名 的反向查找表
            HEXAGRAM_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
            
            def generate_binary_representation(number: int, length: int = 3) -> str:
                return bin(number)[2:].zfill(length)[::-1]
            
            TRIGRAM_BINARY_MAP = {
                generate_binary_representation(i): name 
                for i, name in enumerate(HEXAGRAM_NAMES)
            }
            
            def get_hexagram_details_from_binary_enhanced(binary_str: str):
                """根据六爻二进制串，反查卦名、上下卦、六爻信息"""
                upper_bin = binary_str[:3]
                lower_bin = binary_str[3:]

                upper_name = TRIGRAM_BINARY_MAP.get(upper_bin, "未知")
                lower_name = TRIGRAM_BINARY_MAP.get(lower_bin, "未知")

                full_name_key = f"{upper_name}{lower_name}"
                
                # 简化的卦名映射（实际应该从constants导入完整映射）
                gua_64_simple = {
                    '乾乾': '乾为天', '乾兑': '天泽履', '乾离': '天火同人', '乾震': '天雷无妄',
                    '乾巽': '天风姤', '乾坎': '天水讼', '乾艮': '天山遁', '乾坤': '天地否',
                    '兑乾': '泽天夬', '兑兑': '兑为泽', '兑离': '泽火革', '兑震': '泽雷随',
                    '兑巽': '泽风大过', '兑坎': '泽水困', '兑艮': '泽山咸', '兑坤': '泽地萃',
                    '离乾': '火天大有', '离兑': '火泽睽', '离离': '离为火', '离震': '火雷噬嗑',
                    '离巽': '火风鼎', '离坎': '火水未济', '离艮': '火山旅', '离坤': '火地晋',
                    '震乾': '雷天大壮', '震兑': '雷泽归妹', '震离': '雷火丰', '震震': '震为雷',
                    '震巽': '雷风恒', '震坎': '雷水解', '震艮': '雷山小过', '震坤': '雷地豫',
                    '巽乾': '风天小畜', '巽兑': '风泽中孚', '巽离': '风火家人', '巽震': '风雷益',
                    '巽巽': '巽为风', '巽坎': '风水涣', '巽艮': '风山渐', '巽坤': '风地观',
                    '坎乾': '水天需', '坎兑': '水泽节', '坎离': '水火既济', '坎震': '水雷屯',
                    '坎巽': '水风井', '坎坎': '坎为水', '坎艮': '水山蹇', '坎坤': '水地比',
                    '艮乾': '山天大畜', '艮兑': '山泽损', '艮离': '山火贲', '艮震': '山雷颐',
                    '艮巽': '山风蛊', '艮坎': '山水蒙', '艮艮': '艮为山', '艮坤': '山地剥',
                    '坤乾': '地天泰', '坤兑': '地泽临', '坤离': '地火明夷', '坤震': '地雷复',
                    '坤巽': '地风升', '坤坎': '地水师', '坤艮': '地山谦', '坤坤': '坤为地'
                }
                
                full_name = gua_64_simple.get(full_name_key, f"{upper_name}{lower_name}卦")
                
                return {
                    "name": full_name,
                    "upper_trigram": upper_name,
                    "lower_trigram": lower_name,
                    "yao_binary": binary_str,
                    "liuyao": [],  # 简化版本，保持为空以使用现有显示逻辑
                }
            
            # 获取本卦和变卦的详细信息
            ben_gua_details = get_hexagram_details_from_binary_enhanced(ben_gua_binary)
            bian_gua_details = get_hexagram_details_from_binary_enhanced(bian_gua_binary)
            
            # 修改API结果 - 保留真实的时间四柱信息，只更新说明
            api_result['query_time']['gregorian'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 保留原有的农历时间和干支信息，只在农历时间后添加标注
            original_lunar = api_result['query_time']['lunar']
            api_result['query_time']['lunar'] = f"{original_lunar} (手工指定卦象)"
            # 保留真实的四柱干支信息
            api_result['hexagram']['original'] = ben_gua_details
            api_result['hexagram']['changed'] = bian_gua_details
            api_result['hexagram']['moving_lines'] = moving_lines  # 支持多个动爻
            
            return api_result
            
    except Exception as e:
        # 如果API调用失败，使用简化版本
        pass
    
    # 简化版本的回退逻辑
    HEXAGRAM_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
    
    def generate_binary_representation(number: int, length: int = 3) -> str:
        return bin(number)[2:].zfill(length)[::-1]
    
    TRIGRAM_BINARY_MAP = {
        generate_binary_representation(i): name 
        for i, name in enumerate(HEXAGRAM_NAMES)
    }
    
    def get_hexagram_details_from_binary(binary_str: str):
        upper_bin = binary_str[:3]
        lower_bin = binary_str[3:]

        upper_name = TRIGRAM_BINARY_MAP.get(upper_bin, "未知")
        lower_name = TRIGRAM_BINARY_MAP.get(lower_bin, "未知")
        
        full_name = f"{upper_name}{lower_name}卦"
        
        return {
            "name": full_name,
            "upper_trigram": upper_name,
            "lower_trigram": lower_name,
            "yao_binary": binary_str,
            "liuyao": [],
        }
    
    # 获取本卦和变卦的详细信息
    ben_gua_details = get_hexagram_details_from_binary(ben_gua_binary)
    bian_gua_details = get_hexagram_details_from_binary(bian_gua_binary)
    
    # 构建结果 - 使用真实时间四柱
    current_time = datetime.now()
    
    # 尝试获取真实的时间四柱信息
    try:
        # 导入时间转换服务
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from services.time_converter import LunarDateTimeConverter
        
        converter = LunarDateTimeConverter(current_time)
        basic_info = converter.get_basic_info()
        ganzhi_info = converter.get_ganzhi_info()
        
        lunar_time = f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时 (手工指定卦象)"
        real_ganzhi = ganzhi_info
    except Exception:
        # 如果时间转换失败，使用简化信息
        lunar_time = "手工指定模式"
        real_ganzhi = {
            "year_gz": "手工",
            "month_gz": "指定", 
            "day_gz": "模式",
            "hour_gz": "排盘"
        }
    
    result = {
        "query_time": {
            "gregorian": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar": lunar_time,
            "ganzhi": real_ganzhi
        },
        "hexagram": {
            "original": ben_gua_details,
            "changed": bian_gua_details,
            "moving_lines": moving_lines  # 支持多个动爻
        }
    }
    
    return result

# 在脚本开始时设置（Streamlit 每次运行脚本都会执行此段）
if _parse_ctrlc_option():
    try:
        signal.signal(signal.SIGINT, _sigint_handler)
    except Exception:
        # 某些环境下可能不支持信号设置，忽略即可
        pass

st.set_page_config(page_title="六爻排盘", layout="wide")

# --- 核心辅助函数，用于生成精美的卦象HTML (这部分无需修改) ---
def display_hexagram_visual(hex_data: dict, moving_lines: list = None):
    """
    使用HTML和CSS动态生成一个精美的、对齐的卦象表格
    支持多个动爻的显示
    """
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

        # 2. 动爻标志 (O/X) - 支持多个动爻
        indicator_text = "&nbsp;"
        if moving_lines and yao_position in moving_lines:
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

# --- 新增：起卦方式选择 ---
# 初始化session state
if "divination_mode" not in st.session_state:
    st.session_state.divination_mode = "时间起卦"

divination_mode = st.radio(
    "选择起卦方式",
    ["时间起卦", "手工指定", "卦名起卦"],
    index=0,
    horizontal=True,
    key="divination_mode"
)

if divination_mode == "时间起卦":
    # 原有的时间起卦界面
    with st.container():
        # 初始化session state
        if "use_current_time" not in st.session_state:
            st.session_state.use_current_time = True
            
        use_current_time = st.checkbox("使用当前时间进行排盘", value=True, key="use_current_time")
        target_datetime = None

        if not use_current_time:
            col1, col2 = st.columns(2)
            with col1:
                d = st.date_input("选择日期", datetime.now(), min_value=datetime(1800, 1, 1), max_value=datetime(2100, 12, 31))
            with col2:
                t = st.time_input("选择时间", datetime.now().time())
            target_datetime = datetime.combine(d, t)
        else:
            target_datetime = datetime.now()
            st.info(f"当前起卦时间: {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

elif divination_mode == "手工指定":  # 手工指定模式
    st.subheader("手工指定六爻")
    st.caption("从下往上依次指定六个爻位的阴阳和动静")
    
    # 爻位选择
    yao_options = ["少阳 (阳爻)", "少阴 (阴爻)", "老阳 (阳爻动)", "老阴 (阴爻动)"]
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    
    # 创建两列布局：左侧选择，右侧预览
    col_select, col_preview = st.columns([2, 1])
    
    with col_select:
        st.write("**爻位设置**")
        manual_yaos = []
        
        # 从上爻到初爻垂直排列（符合传统六爻显示习惯）
        for i in range(5, -1, -1):  # 从上爻(5)到初爻(0)
            yao_choice = st.selectbox(
                f"{yao_names[i]}",
                yao_options,
                index=0,
                key=f"yao_{i+1}",
                help=f"设置{yao_names[i]}的阴阳和动静"
            )
            manual_yaos.insert(0, yao_choice)  # 插入到开头，保持初爻到上爻的顺序
    
    with col_preview:
        st.write("**卦象预览**")
        
        # 使用Streamlit原生组件显示卦象预览
        with st.container():
            # 创建一个带边框的容器效果
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 2px solid #e9ecef; text-align: center;'>
            """, unsafe_allow_html=True)
            
            for i in range(5, -1, -1):  # 从上爻到初爻显示
                yao_type = manual_yaos[i]
                
                # 基础爻线符号
                if "阳爻" in yao_type:
                    symbol = "━━━━━━"
                else:
                    symbol = "━━  ━━"
                
                # 动爻标记
                if "动" in yao_type:
                    if "阳爻" in yao_type:
                        moving_symbol = " 〇"  # 白圆圈表示阳动
                    else:
                        moving_symbol = " ×"   # 叉号表示阴动
                else:
                    moving_symbol = ""
                
                # 使用code格式显示爻线，确保等宽字体
                yao_display = f"`{symbol}`{moving_symbol} {yao_names[i]}"
                st.markdown(yao_display)
            
            st.markdown("</div>", unsafe_allow_html=True)

else:  # 卦名起卦模式
    st.subheader("卦名起卦")
    st.caption("直接选择本卦与变卦的上卦与下卦")

    trigram_names = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

    col_ben, col_bian = st.columns(2)

    with col_ben:
        st.write("本卦选择")
        upper_original = st.selectbox("本卦上卦", trigram_names, index=0, key="name_upper_original")
        lower_original = st.selectbox("本卦下卦", trigram_names, index=7, key="name_lower_original")

    with col_bian:
        st.write("变卦选择")
        upper_changed = st.selectbox("变卦上卦", trigram_names, index=0, key="name_upper_changed")
        lower_changed = st.selectbox("变卦下卦", trigram_names, index=7, key="name_lower_changed")

    # 简要预览（按选定卦名构造爻线）
    def _name_to_bin_map():
        # 与服务端一致的三爻二进制生成方式
        def gen(number: int, length: int = 3) -> str:
            return bin(number)[2:].zfill(length)[::-1]
        return {name: gen(i) for i, name in enumerate(trigram_names)}

    NAME_TO_BIN = _name_to_bin_map()
    ben_bin_preview = NAME_TO_BIN[upper_original] + NAME_TO_BIN[lower_original]
    bian_bin_preview = NAME_TO_BIN[upper_changed] + NAME_TO_BIN[lower_changed]

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("本卦预览")
        for i in range(6):
            ch = ben_bin_preview[i]
            symbol = "━━━━━━" if ch == '0' else "━━  ━━"
            st.markdown(f"`{symbol}`")
    with col_p2:
        st.write("变卦预览")
        for i in range(6):
            ch = bian_bin_preview[i]
            symbol = "━━━━━━" if ch == '0' else "━━  ━━"
            st.markdown(f"`{symbol}`")

def create_name_based_hexagram_result(upper_original: str, lower_original: str, upper_changed: str, lower_changed: str):
    """
    根据选择的卦名（上下卦）创建卦象结果，自动计算动爻。
    """
    HEXAGRAM_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

    def generate_binary_representation(number: int, length: int = 3) -> str:
        return bin(number)[2:].zfill(length)[::-1]

    NAME_TO_BIN = {name: generate_binary_representation(i) for i, name in enumerate(HEXAGRAM_NAMES)}

    ben_gua_binary = NAME_TO_BIN.get(upper_original, '000') + NAME_TO_BIN.get(lower_original, '111')
    bian_gua_binary = NAME_TO_BIN.get(upper_changed, '000') + NAME_TO_BIN.get(lower_changed, '111')

    # 计算动爻：两卦二进制位不同的位置即为动爻
    moving_lines = []
    for i in range(6):
        if ben_gua_binary[i] != bian_gua_binary[i]:
            moving_lines.append(6 - i)  # 与显示逻辑一致：1为初爻，6为上爻

    try:
        api_url = st.secrets["API_ENDPOINT"]
        api_key = st.secrets["API_KEY"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {"target_time": datetime.now().isoformat()}
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            api_result = response.json()

            # 建立二进制 -> 卦名 的反查与细节
            TRIGRAM_BINARY_MAP = {
                generate_binary_representation(i): name 
                for i, name in enumerate(HEXAGRAM_NAMES)
            }

            def get_hexagram_details_from_binary_enhanced(binary_str: str):
                upper_bin = binary_str[:3]
                lower_bin = binary_str[3:]
                upper_name = TRIGRAM_BINARY_MAP.get(upper_bin, "未知")
                lower_name = TRIGRAM_BINARY_MAP.get(lower_bin, "未知")
                full_name_key = f"{upper_name}{lower_name}"
                gua_64_simple = {
                    '乾乾': '乾为天', '乾兑': '天泽履', '乾离': '天火同人', '乾震': '天雷无妄',
                    '乾巽': '天风姤', '乾坎': '天水讼', '乾艮': '天山遁', '乾坤': '天地否',
                    '兑乾': '泽天夬', '兑兑': '兑为泽', '兑离': '泽火革', '兑震': '泽雷随',
                    '兑巽': '泽风大过', '兑坎': '泽水困', '兑艮': '泽山咸', '兑坤': '泽地萃',
                    '离乾': '火天大有', '离兑': '火泽睽', '离离': '离为火', '离震': '火雷噬嗑',
                    '离巽': '火风鼎', '离坎': '火水未济', '离艮': '火山旅', '离坤': '火地晋',
                    '震乾': '雷天大壮', '震兑': '雷泽归妹', '震离': '雷火丰', '震震': '震为雷',
                    '震巽': '雷风恒', '震坎': '雷水解', '震艮': '雷山小过', '震坤': '雷地豫',
                    '巽乾': '风天小畜', '巽兑': '风泽中孚', '巽离': '风火家人', '巽震': '风雷益',
                    '巽巽': '巽为风', '巽坎': '风水涣', '巽艮': '风山渐', '巽坤': '风地观',
                    '坎乾': '水天需', '坎兑': '水泽节', '坎离': '水火既济', '坎震': '水雷屯',
                    '坎巽': '水风井', '坎坎': '坎为水', '坎艮': '水山蹇', '坎坤': '水地比',
                    '艮乾': '山天大畜', '艮兑': '山泽损', '艮离': '山火贲', '艮震': '山雷颐',
                    '艮巽': '山风蛊', '艮坎': '山水蒙', '艮艮': '艮为山', '艮坤': '山地剥',
                    '坤乾': '地天泰', '坤兑': '地泽临', '坤离': '地火明夷', '坤震': '地雷复',
                    '坤巽': '地风升', '坤坎': '地水师', '坤艮': '地山谦', '坤坤': '坤为地'
                }
                full_name = gua_64_simple.get(full_name_key, f"{upper_name}{lower_name}卦")
                return {
                    "name": full_name,
                    "upper_trigram": upper_name,
                    "lower_trigram": lower_name,
                    "yao_binary": binary_str,
                    "liuyao": [],
                }

            ben_gua_details = get_hexagram_details_from_binary_enhanced(ben_gua_binary)
            bian_gua_details = get_hexagram_details_from_binary_enhanced(bian_gua_binary)

            api_result['query_time']['gregorian'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            original_lunar = api_result['query_time']['lunar']
            api_result['query_time']['lunar'] = f"{original_lunar} (卦名起卦)"
            api_result['hexagram']['original'] = ben_gua_details
            api_result['hexagram']['changed'] = bian_gua_details
            api_result['hexagram']['moving_lines'] = moving_lines
            return api_result

    except Exception:
        pass

    # 回退：使用本地时间转换服务，保持真实四柱
    current_time = datetime.now()
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from services.time_converter import LunarDateTimeConverter
        converter = LunarDateTimeConverter(current_time)
        basic_info = converter.get_basic_info()
        ganzhi_info = converter.get_ganzhi_info()
        lunar_time = f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时 (卦名起卦)"
        real_ganzhi = ganzhi_info
    except Exception:
        lunar_time = "卦名起卦"
        real_ganzhi = {"year_gz": "手工", "month_gz": "指定", "day_gz": "模式", "hour_gz": "排盘"}

    # 建立细节
    TRIGRAM_BINARY_MAP = {
        generate_binary_representation(i): name 
        for i, name in enumerate(HEXAGRAM_NAMES)
    }

    def get_hexagram_details_from_binary(binary_str: str):
        upper_name = TRIGRAM_BINARY_MAP.get(binary_str[:3], "未知")
        lower_name = TRIGRAM_BINARY_MAP.get(binary_str[3:], "未知")
        return {
            "name": f"{upper_name}{lower_name}卦",
            "upper_trigram": upper_name,
            "lower_trigram": lower_name,
            "yao_binary": binary_str,
            "liuyao": [],
        }

    return {
        "query_time": {
            "gregorian": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar": lunar_time,
            "ganzhi": real_ganzhi
        },
        "hexagram": {
            "original": get_hexagram_details_from_binary(ben_gua_binary),
            "changed": get_hexagram_details_from_binary(bian_gua_binary),
            "moving_lines": moving_lines
        }
    }

# --- 主要修改部分：排盘按钮的逻辑 ---
# 初始化result变量
result = None

if st.button("开始排盘", type="primary", use_container_width=True):

    if divination_mode == "时间起卦":
        # 原有的API调用逻辑
        # 从secrets中读取API配置
        api_url = st.secrets["API_ENDPOINT"]
        api_key = st.secrets["API_KEY"]

        # 准备API请求的头部和载荷
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
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
            else:
                # 如果API返回错误，则显示错误信息
                st.error(f"API调用失败，状态码: {response.status_code}")
                st.json(response.json())
                result = None

        except requests.exceptions.RequestException as e:
            st.error(f"网络请求失败，请检查API服务是否已启动并且地址正确。")
            st.error(f"错误详情: {e}")
            result = None

    elif divination_mode == "手工指定":
        try:
            with st.spinner("正在处理手工指定的卦象..."):
                result = create_manual_hexagram_result(manual_yaos)
        except Exception as e:
            st.error(f"处理手工指定卦象时出错: {e}")
            result = None
    else:  # 卦名起卦模式
        try:
            with st.spinner("正在处理卦名起卦..."):
                result = create_name_based_hexagram_result(
                    st.session_state.get("name_upper_original", '乾'),
                    st.session_state.get("name_lower_original", '坤'),
                    st.session_state.get("name_upper_changed", '乾'),
                    st.session_state.get("name_lower_changed", '坤'),
                )
        except Exception as e:
            st.error(f"处理卦名起卦时出错: {e}")
            result = None

# 显示结果（两种模式共用）
if result:
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
    
    # 显示动爻信息
    moving_lines = hex_info.get('moving_lines', [])
    if not moving_lines and 'moving_line' in hex_info and hex_info['moving_line']:
        moving_lines = [hex_info['moving_line']]  # 兼容旧格式
    
    if moving_lines:
        moving_count = len(moving_lines)
        moving_positions = "、".join([f"{pos}爻" for pos in moving_lines])
        st.info(f"🔄 **动爻信息**: 共 {moving_count} 个动爻，位置：{moving_positions}")
    else:
        st.info("🔄 **动爻信息**: 无动爻")
    
    col_ben, col_bian = st.columns(2)

    with col_ben:
        with st.container(border=True):
            st.header("本卦")
            display_hexagram_visual(hex_info['original'], moving_lines)

    with col_bian:
        with st.container(border=True):
            st.header("变卦")
            display_hexagram_visual(hex_info['changed'])