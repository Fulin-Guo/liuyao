# liuyao/calculator.py
from typing import Tuple, Dict
from . import constants  # 使用相对导入

class HexagramCalculator:
    """卦象计算器"""
    @staticmethod
    def get_tiangan_number(gan: str) -> int:
        """获取天干序号"""
        return constants.TIANGAN.index(gan) + 1
    
    @staticmethod
    def get_dizhi_number(zhi: str, is_month: bool = False) -> int:
        """获取地支序号"""
        base = constants.DIZHI.index(zhi) + 1
        return (base + 10) % 12 + 1 if is_month else base
    
    @staticmethod
    def calculate_hexagram_indices(parameters: Dict) -> Tuple[int, int, int]:
        """
        计算卦象索引 (上卦、下卦、动爻).
        这里的计算方法对应梅花易数等时间起卦法.
        上卦 = (年支序 + 月数 + 日数) % 8 (余数为0则取8)
        下卦 = (年支序 + 月数 + 日数 + 时支序) % 8 (余数为0则取8)
        动爻 = (年支序 + 月数 + 日数 + 时支序) % 6 (余数为0则取6)
        """
        sum_base = parameters['dizhi_year'] + parameters['month'] + parameters['day']
        upper = sum_base % 8 or 8
        lower = (sum_base + parameters['dizhi_hour']) % 8 or 8
        moving_line = (sum_base + parameters['dizhi_hour']) % 6 or 6
        return upper, lower, moving_line
    
    @staticmethod
    def generate_binary_representation(number: int, length: int = 3) -> str:
        """
        根据索引生成三爻的二进制表示 (0-7 对应 '000' 到 '111').
        注意:这里的number是 (卦序-1).结果[::-1]表示爻序从下往上.
        例如: 乾卦序为1, number为0, bin(0) -> '0', zfill(3) -> '000', [::-1] -> '000'.
              坤卦序为8, number为7, bin(7) -> '111', zfill(3) -> '111', [::-1] -> '111'.
        这是一种特定的二进制表示方法，不直接对应传统阴阳爻(如阳1阴0).
        """
        return bin(number)[2:].zfill(length)[::-1]
    
    @classmethod
    def calculate_changes(cls, upper_idx: int, lower_idx: int, moving_line: int) -> Tuple[str, str]:
        """
        计算本卦和变卦的六爻二进制表示.
        upper_idx, lower_idx 为1-8的卦序.
        moving_line 为1-6的动爻位置 (从下往上数).
        """
        # upper_idx-1 和 lower_idx-1 转换为0-7的数字用于二进制表示
        ben_gua_upper_bin = cls.generate_binary_representation(upper_idx - 1)
        ben_gua_lower_bin = cls.generate_binary_representation(lower_idx - 1)
        
        # 上卦二进制 + 下卦二进制
        ben_gua = ben_gua_upper_bin + ben_gua_lower_bin

        bian_list = list(ben_gua)
        # 动爻位置: moving_line 是1-6, 列表索引是0-5.
        # -moving_line (如动爻1对应列表-1即末位，动爻6对应列表-6即首位)
        # 这表示您的爻排列中，字符串的首位是第6爻(上爻)，末位是第1爻(初爻).
        change_index = len(bian_list) - moving_line 
        bian_list[change_index] = str(1 - int(bian_list[change_index])) # 爻变 0->1, 1->0
        
        return ben_gua, "".join(bian_list)