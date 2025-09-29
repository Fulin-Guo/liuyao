# app/services/divination_service.py
from datetime import datetime
from typing import Dict, Any, Tuple, List

from . import constants
from .time_converter import LunarDateTimeConverter

# --- 从 calculator.py 移植过来的核心计算逻辑 ---
class HexagramCalculator:
    # ... (这部分和原来一样，为保持完整性，请保留您原来的代码)
    @staticmethod
    def get_tiangan_number(gan: str) -> int:
        return constants.TIANGAN.index(gan) + 1
    
    @staticmethod
    def get_dizhi_number(zhi: str, is_month: bool = False) -> int:
        base = constants.DIZHI.index(zhi) + 1
        return (base + 10) % 12 + 1 if is_month else base
    
    @staticmethod
    def calculate_hexagram_indices(parameters: Dict) -> Tuple[int, int, int]:
        sum_base = parameters['dizhi_year'] + parameters['month'] + parameters['day']
        upper = sum_base % 8 or 8
        lower = (sum_base + parameters['dizhi_hour']) % 8 or 8
        moving_line = (sum_base + parameters['dizhi_hour']) % 6 or 6
        return upper, lower, moving_line
    
    @staticmethod
    def generate_binary_representation(number: int, length: int = 3) -> str:
        # 爻序从下往上，此方法生成的二进制串，第一位是上爻，最后一位是初爻
        # 乾(1->num 0)->'000', 兑(2->num 1)->'100', 离(3->num 2)->'010', 震(4->num 3)->'110'
        # 巽(5->num 4)->'001', 坎(6->num 5)->'101', 艮(7->num 6)->'011', 坤(8->num 7)->'111'
        return bin(number)[2:].zfill(length)[::-1]
    
    @classmethod
    def calculate_changes(cls, upper_idx: int, lower_idx: int, moving_line: int) -> Tuple[str, str]:
        ben_gua_upper_bin = cls.generate_binary_representation(upper_idx - 1)
        ben_gua_lower_bin = cls.generate_binary_representation(lower_idx - 1)
        ben_gua = ben_gua_upper_bin + ben_gua_lower_bin
        bian_list = list(ben_gua)
        change_index = len(bian_list) - moving_line
        bian_list[change_index] = str(1 - int(bian_list[change_index]))
        return ben_gua, "".join(bian_list)

# --- 新增的辅助函数 ---
def calculate_liushen(day_tiangan: str) -> List[str]:
    """
    根据日干计算六神配置
    :param day_tiangan: 日干（甲、乙、丙等）
    :return: 六爻对应的六神列表（从初爻到上爻）
    """
    start_index = constants.RIGANQI_LIUSHEN.get(day_tiangan, 0)
    liushen_sequence = []
    
    # 从初爻到上爻，按六神顺序循环配置
    for i in range(6):
        liushen_index = (start_index + i) % 6
        liushen_sequence.append(constants.LIUSHEN[liushen_index])
    
    return liushen_sequence

def _get_hexagram_details_from_binary(binary_str: str, day_tiangan: str = None) -> Dict[str, Any]:
    """根据六爻二进制串，反查卦名、上下卦、六爻信息"""
    
    # 建立二进制 -> 卦名 的反向查找表
    TRIGRAM_BINARY_MAP = {
        HexagramCalculator.generate_binary_representation(i): name 
        for i, name in enumerate(constants.HEXAGRAM_NAMES)
    }

    upper_bin = binary_str[:3]
    lower_bin = binary_str[3:]

    upper_name = TRIGRAM_BINARY_MAP.get(upper_bin, "未知")
    lower_name = TRIGRAM_BINARY_MAP.get(lower_bin, "未知")

    full_name_key = f"{upper_name}{lower_name}"
    full_name = constants.GUA_64.get(full_name_key, f"未知卦 ({full_name_key})")
    
    base_name_for_liuyao = full_name.split('（')[0]
    liuyao_info = constants.GUA_LIUYAO.get(base_name_for_liuyao, {}).get('yao_info', [])
    gong = constants.GUA_LIUYAO.get(base_name_for_liuyao, {}).get('gong', '未知宫')
    
    # 计算六神（如果提供了日干）
    liushen_list = []
    if day_tiangan:
        liushen_list = calculate_liushen(day_tiangan)

    return {
        "name": full_name,
        "upper_trigram": upper_name,
        "lower_trigram": lower_name,
        "yao_binary": binary_str,
        "gong": gong,
        "liuyao": liuyao_info,
        "liushen": liushen_list,
    }

# --- 服务函数，替代 run_divination ---
def perform_divination(target_time: datetime = None) -> Dict[str, Any]:
    """
    执行一次六爻排盘，并返回结构化的字典数据。
    :param target_time: 可选的特定时间，如果为 None，则使用当前时间。
    :return: 包含所有排盘结果的字典。
    """
    if target_time is None:
        target_time = datetime.now()

    converter = LunarDateTimeConverter(target_time)
    basic_info = converter.get_basic_info()
    ganzhi_info = converter.get_ganzhi_info()
    
    calculation_params = {
        'dizhi_year': HexagramCalculator.get_dizhi_number(ganzhi_info['year_gz'][1]),
        'month': abs(basic_info['month']),
        'day': basic_info['day'],
        'dizhi_hour': HexagramCalculator.get_dizhi_number(ganzhi_info['hour_gz'][1])
    }
    
    upper_idx, lower_idx, moving_line = HexagramCalculator.calculate_hexagram_indices(calculation_params)
    ben_gua_bin, bian_gua_bin = HexagramCalculator.calculate_changes(upper_idx, lower_idx, moving_line)
    
    # 获取日干用于计算六神
    day_tiangan = ganzhi_info['day_gz'][0]
    
    # 使用辅助函数获取本卦和变卦的完整信息
    ben_gua_details = _get_hexagram_details_from_binary(ben_gua_bin, day_tiangan)
    bian_gua_details = _get_hexagram_details_from_binary(bian_gua_bin, day_tiangan)

    result = {
        "query_time": {
            "gregorian": target_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar": f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时",
            "ganzhi": ganzhi_info
        },
        "hexagram": {
            "original": ben_gua_details,
            "changed": bian_gua_details,
            "moving_line": moving_line
        }
    }
    
    return result