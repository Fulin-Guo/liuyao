from liuyao.time_converter import LunarDateTimeConverter
from liuyao.calculator import HexagramCalculator
from liuyao.formatter import ResultFormatter
from liuyao import constants # 导入常量模块以访问 HEXAGRAM_NAMES

def run_divination():
    """执行一次起卦流程"""
    # 初始化核心组件
    converter = LunarDateTimeConverter()
    # HexagramCalculator 的方法都是静态的，不需要实例化
    
    # 获取基础数据
    basic_info = converter.get_basic_info()
    ganzhi_info = converter.get_ganzhi_info()
    
    # 准备计算卦象的参数
    # 注意: calculator.get_dizhi_number 对于 month 的处理逻辑 (is_month=True)
    # 在原代码中并未将 is_month 设为 True 来获取月份地支序数，而是直接用了农历月份数字。
    # 梅花易数中，上卦=(年支序+月数+日数)%8, 月数通常是农历月数。
    # 时支序参数是正确的。年支序也是地支序。
    calculation_params = {
        'dizhi_year': HexagramCalculator.get_dizhi_number(ganzhi_info['year_gz'][1]), # 取地支字符
        'month': basic_info['month'], # 直接用农历月数
        'day': basic_info['day'],     # 直接用农历日数
        'dizhi_hour': HexagramCalculator.get_dizhi_number(ganzhi_info['hour_gz'][1]) # 取地支字符
    }
    
    # 计算卦象索引 (上卦序, 下卦序, 动爻)
    upper_idx, lower_idx, moving_line = HexagramCalculator.calculate_hexagram_indices(calculation_params)
    
    # 生成本卦和变卦的六爻二进制表示
    # upper_idx 和 lower_idx 是1-8的卦序
    ben_gua_6yao_str, bian_gua_6yao_str = HexagramCalculator.calculate_changes(upper_idx, lower_idx, moving_line)
    print(ben_gua_6yao_str,bian_gua_6yao_str)
    
    # 准备卦象数据用于格式化输出
    hexagram_data = {
        # constants.HEXAGRAM_NAMES 列表索引是 0-7, 而 upper_idx/lower_idx 是 1-8
        'upper_hexagram': f"{constants.HEXAGRAM_NAMES[upper_idx-1]} {HexagramCalculator.generate_binary_representation(upper_idx-1)}",
        'lower_hexagram': f"{constants.HEXAGRAM_NAMES[lower_idx-1]} {HexagramCalculator.generate_binary_representation(lower_idx-1)}",
        'moving_line': moving_line,
        'ben_gua': ben_gua_6yao_str,
        'bian_gua': bian_gua_6yao_str
    }
    
    # 格式化并输出结果
    formatted_output = ResultFormatter.format_output(basic_info, ganzhi_info, hexagram_data)
    print(formatted_output)

if __name__ == "__main__":
    run_divination()