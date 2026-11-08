"""
应用配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 阿里云短信服务配置
ALIYUN_SMS_ACCESS_KEY_ID = os.getenv("ALIYUN_SMS_ACCESS_KEY_ID", "")
ALIYUN_SMS_ACCESS_KEY_SECRET = os.getenv("ALIYUN_SMS_ACCESS_KEY_SECRET", "")
ALIYUN_SMS_SIGN_NAME = os.getenv("ALIYUN_SMS_SIGN_NAME", "")
ALIYUN_SMS_ENDPOINT = "dypnsapi.aliyuncs.com"

# 短信模板代码
SMS_TEMPLATE_REGISTER = "100001"  # 注册/登录
SMS_TEMPLATE_CHANGE_PHONE = "100002"  # 修改手机号
SMS_TEMPLATE_RESET_PASSWORD = "100003"  # 重置密码
SMS_TEMPLATE_BIND_NEW_PHONE = "100004"  # 绑定新手机号
SMS_TEMPLATE_VERIFY_BIND_PHONE = "100005"  # 验证绑定手机号

# 短信验证码配置
SMS_CODE_LENGTH = 6  # 验证码长度
SMS_VALID_TIME = 300  # 验证码有效期（秒），5分钟
SMS_SEND_INTERVAL = 60  # 发送间隔（秒），60秒
SMS_CODE_TYPE = 1  # 验证码类型：1-纯数字

# ==================== 火山方舟AI配置 ====================
VOLCENGINE_ARK_API_KEY = os.getenv("VOLCENGINE_ARK_API_KEY", "")
VOLCENGINE_ARK_MODEL = os.getenv("VOLCENGINE_ARK_MODEL", "doubao-seed-1-8-251228")
VOLCENGINE_ARK_BASE_URL = os.getenv("VOLCENGINE_ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")


# Paid services require explicit opt-in as well as locally configured credentials.
SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
