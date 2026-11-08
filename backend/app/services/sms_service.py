"""
短信服务模块
使用阿里云号码认证服务（DYPNS）发送和验证短信验证码
"""
from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models
import json
from app.config import (
    SMS_ENABLED,
    ALIYUN_SMS_ACCESS_KEY_ID,
    ALIYUN_SMS_ACCESS_KEY_SECRET,
    ALIYUN_SMS_ENDPOINT,
    ALIYUN_SMS_SIGN_NAME,
    SMS_TEMPLATE_REGISTER,
    SMS_TEMPLATE_CHANGE_PHONE,
    SMS_TEMPLATE_RESET_PASSWORD,
    SMS_TEMPLATE_BIND_NEW_PHONE,
    SMS_TEMPLATE_VERIFY_BIND_PHONE,
    SMS_CODE_LENGTH,
    SMS_VALID_TIME,
    SMS_SEND_INTERVAL,
    SMS_CODE_TYPE
)


# 场景到模板代码的映射
SCENE_TO_TEMPLATE = {
    "register": SMS_TEMPLATE_REGISTER,
    "login": SMS_TEMPLATE_REGISTER,
    "change_phone": SMS_TEMPLATE_CHANGE_PHONE,
    "reset_password": SMS_TEMPLATE_RESET_PASSWORD,
    "bind_new_phone": SMS_TEMPLATE_BIND_NEW_PHONE,
    "verify_bind_phone": SMS_TEMPLATE_VERIFY_BIND_PHONE,
}


def create_client():
    """创建阿里云客户端"""
    if not SMS_ENABLED:
        raise RuntimeError("SMS service disabled; set SMS_ENABLED=true to opt in")
    if not all((ALIYUN_SMS_ACCESS_KEY_ID, ALIYUN_SMS_ACCESS_KEY_SECRET, ALIYUN_SMS_SIGN_NAME)):
        raise RuntimeError("SMS credentials and sign name must be configured locally")
    config = open_api_models.Config(
        access_key_id=ALIYUN_SMS_ACCESS_KEY_ID,
        access_key_secret=ALIYUN_SMS_ACCESS_KEY_SECRET
    )
    config.endpoint = ALIYUN_SMS_ENDPOINT
    return Dypnsapi20170525Client(config)


def translate_error(error_code: str) -> str:
    """将阿里云错误代码转换为用户友好的提示"""
    error_map = {
        "MOBILE_NUMBER_ILLEGAL": "手机号格式不正确",
        "BUSINESS_LIMIT_CONTROL": "发送次数超限，请明天再试",
        "FREQUENCY_FAIL": "发送太频繁，请稍后再试",
        "INVALID_PARAMETERS": "参数错误，请检查输入",
        "SYSTEM_ERROR": "系统错误，请稍后再试",
    }
    return error_map.get(error_code, f"发送失败：{error_code}")


def send_sms(phone: str, scene: str) -> dict:
    """
    发送短信验证码
    
    Args:
        phone: 手机号
        scene: 场景（register/login/reset_password等）
    
    Returns:
        dict: 包含 success 和 message 字段
    """
    try:
        # 验证手机号格式
        if not phone or not phone.startswith("1") or len(phone) != 11:
            return {
                "success": False,
                "message": "手机号格式不正确"
            }
        
        # 获取模板代码
        template_code = SCENE_TO_TEMPLATE.get(scene)
        if not template_code:
            return {
                "success": False,
                "message": f"不支持的场景：{scene}"
            }
        
        # 创建客户端
        client = create_client()
        
        # 构建请求
        send_sms_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=ALIYUN_SMS_SIGN_NAME,
            template_code=template_code,
            code_length=SMS_CODE_LENGTH,
            valid_time=SMS_VALID_TIME,
            interval=SMS_SEND_INTERVAL,
            code_type=SMS_CODE_TYPE,
            template_param=json.dumps({"code": "##code##", "min": "5"})
        )
        
        # 发送请求
        runtime = util_models.RuntimeOptions()
        response = client.send_sms_verify_code_with_options(send_sms_request, runtime)
        
        # 检查响应
        if response.status_code == 200:
            body = response.body
            if body.code == "OK":
                return {
                    "success": True,
                    "message": "验证码发送成功",
                    "request_id": body.request_id
                }
            else:
                error_msg = translate_error(body.code)
                return {
                    "success": False,
                    "message": error_msg,
                    "code": body.code
                }
        else:
            return {
                "success": False,
                "message": f"请求失败，状态码：{response.status_code}"
            }
    
    except Exception as e:
        print(f"发送短信验证码异常：{str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": "短信服务不可用，请检查本地配置"
        }


def check_sms_code(phone: str, code: str) -> dict:
    """
    校验短信验证码
    
    Args:
        phone: 手机号
        code: 验证码
    
    Returns:
        dict: 包含 success 和 message 字段
    """
    try:
        # 验证参数
        if not phone or not phone.startswith("1") or len(phone) != 11:
            return {
                "success": False,
                "message": "手机号格式不正确"
            }
        
        if not code or len(code) != SMS_CODE_LENGTH:
            return {
                "success": False,
                "message": "验证码格式不正确"
            }
        
        # 创建客户端
        client = create_client()
        
        # 构建请求
        check_request = dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(
            phone_number=phone,
            verify_code=code
        )
        
        # 发送请求
        runtime = util_models.RuntimeOptions()
        response = client.check_sms_verify_code_with_options(check_request, runtime)
        
        # 检查响应
        if response.status_code == 200:
            body = response.body
            if body.code == "OK":
                # 检查验证结果
                if hasattr(body, "model") and body.model:
                    verify_result = getattr(body.model, "verify_result", None)
                    if verify_result == "PASS":
                        return {
                            "success": True,
                            "message": "验证码校验成功"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "验证码错误或已过期"
                        }
                else:
                    # 如果没有model字段，检查code是否为OK
                    return {
                        "success": True,
                        "message": "验证码校验成功"
                    }
            else:
                error_msg = translate_error(body.code)
                return {
                    "success": False,
                    "message": error_msg,
                    "code": body.code
                }
        else:
            return {
                "success": False,
                "message": f"请求失败，状态码：{response.status_code}"
            }
    
    except Exception as e:
        print(f"校验短信验证码异常：{str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": "短信校验服务不可用"
        }

