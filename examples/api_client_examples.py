"""
API 调用示例：使用现有服务的三种起卦方式

依赖：requests
环境变量：
- API_ENDPOINT: 例如 http://localhost:8000/divination 或 http://your-host:8000/divination
- API_KEY: 在服务端生成的 API Key（通过请求头 X-API-Key 传入）

运行：
    python examples/api_client_examples.py

说明：
现有 API 端点仅支持“时间起卦”计算（POST /divination）。
对于“手工指定”和“卦名起卦”，示例脚本会：
1) 调用 /divination 获取真实时间与四柱；
2) 在客户端按你的输入生成本卦/变卦及动爻；
3) 将结果与时间四柱合并输出，保持与 WebUI 一致的显示逻辑。
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import requests


# ----------------------------- 基础配置 -----------------------------
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/divination")
API_KEY = os.getenv("API_KEY", "-DlYjQ5uuSGVa63rP10rtvlTn9mCmOsllJroY2gbWqk")


# ---------------------- 八卦与六爻辅助（与前端一致） ----------------------
TRIGRAM_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

def generate_binary_representation(number: int, length: int = 3) -> str:
    """与服务端/前端一致：按下爻→上爻的顺序生成三爻二进制。"""
    return bin(number)[2:].zfill(length)[::-1]

NAME_TO_BIN = {name: generate_binary_representation(i) for i, name in enumerate(TRIGRAM_NAMES)}
BIN_TO_NAME = {v: k for k, v in NAME_TO_BIN.items()}

# 简化的六十四卦映射（与 WebUI 保持一致）
GUA_64_SIMPLE: Dict[str, str] = {
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

def get_hexagram_details_from_binary_enhanced(binary_str: str) -> Dict[str, Any]:
    upper_bin = binary_str[:3]
    lower_bin = binary_str[3:]
    upper_name = BIN_TO_NAME.get(upper_bin, "未知")
    lower_name = BIN_TO_NAME.get(lower_bin, "未知")
    full_name_key = f"{upper_name}{lower_name}"
    full_name = GUA_64_SIMPLE.get(full_name_key, f"{upper_name}{lower_name}卦")
    return {
        "name": full_name,
        "upper_trigram": upper_name,
        "lower_trigram": lower_name,
        "yao_binary": binary_str,
        "liuyao": [],  # 示例中不展开爻辞
    }

def convert_manual_yaos_to_hexagram_data(manual_yaos: List[str]):
    """将六个爻位（初→上）转换为本卦/变卦二进制及动爻列表。"""
    ben_gua_bits: List[str] = []
    moving_lines: List[int] = []
    for i, yao_choice in enumerate(manual_yaos):
        if "阳爻" in yao_choice:
            ben_gua_bits.append('0')  # 阳爻
        else:
            ben_gua_bits.append('1')  # 阴爻
        if "动" in yao_choice:
            moving_lines.append(i + 1)  # 记录动爻位置（1-6）
    ben_gua_binary = ''.join(reversed(ben_gua_bits))  # 组合为上→下顺序
    if not moving_lines:
        bian_gua_binary = ben_gua_binary
    else:
        bian_gua_bits = list(ben_gua_binary)
        for ml in moving_lines:
            idx = 6 - ml
            bian_gua_bits[idx] = str(1 - int(bian_gua_bits[idx]))
        bian_gua_binary = ''.join(bian_gua_bits)
    return ben_gua_binary, bian_gua_binary, moving_lines


# ----------------------------- API 调用封装 -----------------------------
def call_api(target_time_iso: str | None) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    payload = {"target_time": target_time_iso}
    resp = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ----------------------------- 三种方式示例 -----------------------------
def time_divination(target_time: datetime | None = None) -> Dict[str, Any]:
    """时间起卦：直接由服务端计算本卦、变卦与动爻。"""
    target_iso = target_time.isoformat() if target_time else None
    result = call_api(target_iso)
    print("\n[时间起卦] 成功获取结果")
    print_summary(result)
    return result

def manual_divination(manual_yaos: List[str]) -> Dict[str, Any]:
    """手工指定六爻：用 API 获取真实时间/四柱，在本地生成卦象。"""
    api_result = call_api(datetime.now().isoformat())
    ben_bin, bian_bin, moving_lines = convert_manual_yaos_to_hexagram_data(manual_yaos)
    ben = get_hexagram_details_from_binary_enhanced(ben_bin)
    bian = get_hexagram_details_from_binary_enhanced(bian_bin)
    api_result['query_time']['lunar'] = f"{api_result['query_time']['lunar']} (手工指定卦象)"
    api_result['hexagram'] = {"original": ben, "changed": bian, "moving_lines": moving_lines}
    print("\n[手工指定] 成功生成结果（保留真实四柱）")
    print_summary(api_result)
    return api_result

def name_based_divination(upper_original: str, lower_original: str,
                          upper_changed: str, lower_changed: str) -> Dict[str, Any]:
    """卦名起卦：选择上下卦，用 API 获取真实时间/四柱，在本地生成卦象。"""
    api_result = call_api(datetime.now().isoformat())
    ben_bin = NAME_TO_BIN[upper_original] + NAME_TO_BIN[lower_original]
    bian_bin = NAME_TO_BIN[upper_changed] + NAME_TO_BIN[lower_changed]
    moving_lines = [6 - i for i in range(6) if ben_bin[i] != bian_bin[i]]
    ben = get_hexagram_details_from_binary_enhanced(ben_bin)
    bian = get_hexagram_details_from_binary_enhanced(bian_bin)
    api_result['query_time']['lunar'] = f"{api_result['query_time']['lunar']} (卦名起卦)"
    api_result['hexagram'] = {"original": ben, "changed": bian, "moving_lines": moving_lines}
    print("\n[卦名起卦] 成功生成结果（保留真实四柱）")
    print_summary(api_result)
    return api_result


# ----------------------------- 输出整洁摘要 -----------------------------
def print_summary(result: Dict[str, Any]) -> None:
    time_info = result['query_time']
    hex_info = result['hexagram']
    print(f"公历时间: {time_info['gregorian']}")
    print(f"农历时间: {time_info['lunar']}")
    gz = time_info['ganzhi']
    # 四柱（元组/字符串兼容）
    def fmt_gz(v):
        return v if isinstance(v, str) else "".join(v)
    print("四柱干支:")
    print(f"  年柱: {fmt_gz(gz['year_gz'])}")
    print(f"  月柱: {fmt_gz(gz['month_gz'])}")
    print(f"  日柱: {fmt_gz(gz['day_gz'])}")
    print(f"  时柱: {fmt_gz(gz['hour_gz'])}")

    moving_lines = hex_info.get('moving_lines', [])
    if not moving_lines and 'moving_line' in hex_info and hex_info['moving_line']:
        moving_lines = [hex_info['moving_line']]

    print(f"本卦: {hex_info['original']['name']} | 上卦: {hex_info['original']['upper_trigram']} | 下卦: {hex_info['original']['lower_trigram']}")
    print(f"变卦: {hex_info['changed']['name']} | 上卦: {hex_info['changed']['upper_trigram']} | 下卦: {hex_info['changed']['lower_trigram']}")
    print(f"动爻: {'、'.join(str(p)+'爻' for p in moving_lines) if moving_lines else '无'}")
    print(f"本卦二进制: {hex_info['original']['yao_binary']}")
    print(f"变卦二进制: {hex_info['changed']['yao_binary']}")


# ----------------------------- 示例入口 -----------------------------
if __name__ == "__main__":
    print(f"使用 API_ENDPOINT={API_ENDPOINT}")
    print("提示：将 API_KEY 放入环境变量，或直接在脚本顶部修改。\n")

    # 1) 时间起卦（服务端直接计算）
    time_divination(datetime.now())

    # 2) 手工指定六爻（初→上）。可按需修改为你的输入。
    manual_yaos_sample = [
        "少阳 (阳爻)",     # 初爻
        "少阴 (阴爻)",     # 二爻
        "老阳 (阳爻动)",   # 三爻
        "少阴 (阴爻)",     # 四爻
        "老阴 (阴爻动)",   # 五爻
        "少阳 (阳爻)"      # 上爻
    ]
    manual_divination(manual_yaos_sample)

    # 3) 卦名起卦：选择本卦与变卦的上下卦。
    name_based_divination("乾", "坤", "坎", "离")