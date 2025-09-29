# 专业六爻排盘与API服务

本项目是一个专业的六爻排盘工具，提供完整的六爻起卦、排盘和分析功能。支持多种起卦方式，包含完整的纳甲、六亲、六神、世应等传统六爻要素，同时提供Web界面和API接口两种使用方式。

## 🌟 项目特点

### 核心功能
- **完整的六爻排盘系统**: 支持时间起卦、手工指定、卦名起卦三种方式
- **传统六爻要素**: 完整支持纳甲、六亲、六神、世应标记
- **精确的时间转换**: 公历农历转换、天干地支计算
- **专业的卦象分析**: 本卦变卦对比、动爻标记

### 接口方式
- **Web用户界面**: 基于Streamlit构建的直观界面，支持实时排盘和结果展示
- **RESTful API**: 基于FastAPI构建，提供完整的编程接口
- **客户端示例**: 提供Python客户端示例代码

### 技术特色
- **模块化设计**: 清晰的代码结构，易于维护和扩展
- **API认证**: 使用API Key进行安全认证
- **实时重载**: 开发模式支持代码热重载
- **完整文档**: 自动生成的API文档

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
# 方法1: 使用启动脚本 (Windows)
start_services.bat

# 方法2: 使用启动脚本 (Linux/Mac)
./start_services.sh

# 方法3: 手动启动
# 启动API服务 (端口8001)
cd app && uvicorn main:app --reload --port 8001

# 启动Web界面 (端口8503)
streamlit run webui_api.py --server.port 8503
```

### 访问服务
- **Web界面**: http://localhost:8503
- **API文档**: http://localhost:8001/docs
- **API接口**: http://localhost:8001

## 📚 API使用指南

### 认证方式
所有API请求需要在请求头中包含API Key：
```
Authorization: Bearer your-secret-api-key
```

### 生成API Key
```bash
python create_api_key.py
```

### API端点

#### 1. 增强型六爻排盘 (推荐)
**端点**: `POST /enhanced-divination`

支持三种起卦方式：

**时间起卦** (基于当前时间)
```json
{
  "divination_type": "time"
}
```

**手工指定** (手动指定六爻)
```json
{
  "divination_type": "manual",
  "manual_yaos": ["阳爻", "阴爻动", "阳爻", "阴爻", "阳爻动", "阴爻"],
  "target_time": "2024-01-01T10:30:00"
}
```

**卦名起卦** (基于卦名)
```json
{
  "divination_type": "name",
  "upper_original": "乾",
  "lower_original": "坤",
  "upper_changed": "震",
  "lower_changed": "巽",
  "target_time": "2024-01-01T10:30:00"
}
```

#### 2. 基础六爻排盘
**端点**: `POST /divination`
```json
{
  "target_time": "2024-01-01T10:30:00"  // 可选，默认当前时间
}
```

### 响应格式
```json
{
  "divination_type": "时间起卦",
  "query_time": {
    "formatted_time": "2024-01-01 10:30:00",
    "lunar_date": "2023年十一月二十日 巳时",
    "ganzhi_info": {
      "year_gz": "癸卯",
      "month_gz": "甲子",
      "day_gz": "丁巳",
      "hour_gz": "乙巳"
    }
  },
  "hexagram": {
    "original": {
      "name": "天地否",
      "upper_trigram": "乾",
      "lower_trigram": "坤",
      "yao_binary": "111000",
      "gong": "乾宫",
      "yaos": [
        {
          "position": 1,
          "binary": "0",
          "type": "阴爻",
          "liuqin": "妻财",
          "najia": "未土",
          "liushen": "青龙",
          "shi_ying": "世"
        }
        // ... 其他爻位信息
      ]
    },
    "changed": {
      // 变卦信息结构同上
    },
    "moving_line": 3  // 动爻位置
  }
}
```

## 🛠️ 开发指南

### 项目结构
```
liuyao/
├── README.md                   # 项目说明文档
├── requirements.txt            # Python依赖包
├── start_services.bat         # Windows启动脚本
├── start_services.sh          # Linux/Mac启动脚本
├── create_api_key.py          # API Key生成工具
├── liuyao_api.db             # SQLite数据库
├── app/                       # FastAPI应用
│   ├── main.py               # API主入口
│   ├── schemas.py            # 数据模型定义
│   ├── database.py           # 数据库配置
│   ├── crud.py              # 数据库操作
│   ├── dependencies.py      # API依赖项
│   ├── models.py            # SQLAlchemy模型
│   └── services/            # 核心业务逻辑
│       ├── constants.py     # 六爻常量定义
│       ├── time_converter.py # 时间转换服务
│       ├── calculator.py    # 卦象计算器
│       ├── divination_service.py # 基础排盘服务
│       ├── enhanced_divination_service.py # 增强排盘服务
│       └── formatter.py     # 结果格式化
├── examples/                  # 客户端示例
│   ├── api_client_examples.py # 基础API示例
│   └── enhanced_api_client_examples.py # 增强API示例
├── webui.py                  # 直接调用的Web界面
└── webui_api.py             # 基于API的Web界面
```

### 核心模块说明

#### 时间转换 (`time_converter.py`)
- 公历农历转换
- 天干地支计算
- 时辰转换

#### 卦象计算 (`calculator.py`)
- 六爻起卦算法
- 动爻计算
- 变卦生成

#### 排盘服务 (`enhanced_divination_service.py`)
- 纳甲配置
- 六亲关系
- 六神排列
- 世应标记

### 客户端示例
项目提供了完整的Python客户端示例：

```python
from examples.enhanced_api_client_examples import LiuyaoAPIClient

# 创建客户端
client = LiuyaoAPIClient()

# 时间起卦
result = client.time_divination()

# 手工指定
result = client.manual_divination(["阳爻", "阴爻动", "阳爻", "阴爻", "阳爻", "阴爻"])

# 卦名起卦
result = client.name_divination("乾", "坤", "震", "巽")
```

## 🔧 技术栈

- **后端框架**: FastAPI
- **Web界面**: Streamlit
- **数据库**: SQLite
- **时间处理**: lunar_python
- **API文档**: Swagger/OpenAPI
- **认证**: Bearer Token

## 📈 功能特性

### 已实现功能
- ✅ 三种起卦方式（时间、手工、卦名）
- ✅ 完整的六爻要素（纳甲、六亲、六神、世应）
- ✅ 本卦变卦对比
- ✅ 动爻标记
- ✅ Web界面和API接口
- ✅ API认证和文档
- ✅ 客户端示例代码

### 计划功能
- 🔄 卦辞爻辞解释
- 🔄 六爻分析算法
- 🔄 历史记录功能
- 🔄 批量排盘接口
- 🔄 更多起卦方式

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 开发环境设置
1. Fork本项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本项目仅供学习和研究使用，六爻预测结果仅供参考，不构成任何决策建议。
