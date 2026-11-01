"""
短信服务工具：使用阿里云号码认证服务（DYPNS）发送和验证短信验证码
"""
import re
from typing import Dict, Tuple
from app.config import (
    SMS_ENABLED,
    ALIYUN_ACCESS_KEY_ID, 
    ALIYUN_ACCESS_KEY_SECRET, 
    ALIYUN_SMS_ENDPOINT,
    ALIYUN_SMS_SIGN_NAME,
    SMS_TEMPLATE_REGISTER,
    SMS_TEMPLATE_RESET_PASSWORD,
    SMS_TEMPLATE_CHANGE_PHONE,
    SMS_TEMPLATE_BIND_PHONE,
    SMS_TEMPLATE_VERIFY_PHONE,
)


class AliyunSmsClient:
    """阿里云短信客户端"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """获取阿里云客户端单例"""
        if not SMS_ENABLED:
            raise RuntimeError("短信服务未配置，暂不可用")
        if cls._client is None:
            from alibabacloud_dypnsapi20170525.client import Client as DypnsClient
            from alibabacloud_tea_openapi import models as open_api_models
            config = open_api_models.Config(
                access_key_id=ALIYUN_ACCESS_KEY_ID,
                access_key_secret=ALIYUN_ACCESS_KEY_SECRET,
                endpoint=ALIYUN_SMS_ENDPOINT
            )
            cls._client = DypnsClient(config)
        return cls._client


def get_template_code(scene: str) -> str:
    """
    根据场景获取模板CODE
    
    Args:
        scene: 场景名称 (register, reset_password, change_phone, bind_phone, verify_phone)
    
    Returns:
        模板CODE
    """
    scene_map = {
        'register': SMS_TEMPLATE_REGISTER,
        'login': SMS_TEMPLATE_REGISTER,  # 登录使用注册模板
        'reset_password': SMS_TEMPLATE_RESET_PASSWORD,
        'change_phone': SMS_TEMPLATE_CHANGE_PHONE,
        'bind_phone': SMS_TEMPLATE_BIND_PHONE,
        'verify_phone': SMS_TEMPLATE_VERIFY_PHONE
    }
    return scene_map.get(scene, SMS_TEMPLATE_REGISTER)


def send_sms(phone: str, scene: str = 'register') -> Dict[str, any]:
    """
    发送短信验证码（阿里云自动生成验证码）
    
    Args:
        phone: 手机号
        scene: 使用场景 (register, reset_password, change_phone等)
    
    Returns:
        dict: 包含 success (bool), message (str), 可能包含 biz_id (str)
    """
    if not SMS_ENABLED:
        return {'success': False, 'message': '短信服务未配置，暂不可用'}
    try:
        from alibabacloud_dypnsapi20170525 import models as dypns_models
        from alibabacloud_tea_util import models as util_models
        print(f"[SMS] 开始发送验证码: phone={phone}, scene={scene}")
        
        # 获取客户端
        try:
            client = AliyunSmsClient.get_client()
            print(f"[SMS] 客户端初始化成功")
        except Exception as e:
            print(f"[SMS] 客户端初始化失败: {type(e).__name__}: {str(e)}")
            raise
        
        # 构建请求
        request = dypns_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=ALIYUN_SMS_SIGN_NAME,  # 注意：参数名是 sign_name 不是 scheme_name
            template_code=get_template_code(scene),
            template_param='{"code":"##code##","min":"5"}',  # 阿里云自动生成验证码
            code_length=6,  # 6位验证码
            valid_time=300,  # 5分钟有效
            interval=60,  # 60秒发送间隔
            code_type=1  # 1=纯数字
        )
        print(f"[SMS] 请求参数构建完成: template_code={get_template_code(scene)}")
        
        runtime = util_models.RuntimeOptions()
        
        # 发送短信
        print(f"[SMS] 准备调用阿里云API...")
        response = client.send_sms_verify_code_with_options(request, runtime)
        print(f"[SMS] API调用完成: status_code={response.status_code}")
        
        # 检查响应
        body = response.body
        if response.status_code == 200 and body and getattr(body, 'code', None) == 'OK':
            # 获取biz_id（如果有的话）
            biz_id = getattr(getattr(body, 'model', None), 'biz_id', None)
            print(f"[SMS] 发送成功: biz_id={biz_id}")
            result = {
                'success': True,
                'message': '验证码发送成功'
            }
            if biz_id:
                result['biz_id'] = biz_id
            return result
        else:
            error_code = getattr(body, 'code', None) if body else None
            error_message = getattr(body, 'message', None) if body else None
            print(
                f"[SMS] 发送失败: status_code={response.status_code}, "
                f"code={error_code}, message={error_message}"
            )
            message = _friendly_send_error(error_code, error_message)
            return {
                'success': False,
                'message': message
            }
            
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"[SMS] 捕获异常: {error_type}: {error_msg}")
        
        # 打印完整的错误堆栈
        import traceback
        print(f"[SMS] 错误堆栈:\n{traceback.format_exc()}")
        
        # 将阿里云错误转换为用户友好提示
        message = _friendly_send_error(error_msg, error_msg)
        
        return {
            'success': False,
            'message': message
        }


def _friendly_send_error(error_code, error_message) -> str:
    """把阿里云错误码转换成可供登录页展示的提示。"""
    detail = f"{error_code or ''} {error_message or ''}"
    if 'MOBILE_NUMBER_ILLEGAL' in detail or 'InvalidPhoneNumber' in detail:
        return '手机号格式不正确'
    if 'BUSINESS_LIMIT_CONTROL' in detail or 'BusinessLimitControl' in detail:
        return '发送次数超限，请稍后再试'
    if 'FREQUENCY_FAIL' in detail or 'Throttling' in detail or '429' in detail:
        return '发送太频繁，请等待1分钟后再试'
    if 'SignNameNotMatch' in detail or 'SIGN_NAME' in detail:
        return '短信签名未通过，请检查阿里云短信签名配置'
    if 'TemplateNotMatch' in detail or 'TEMPLATE' in detail:
        return '短信模板未通过，请检查阿里云短信模板配置'
    if 'Operation not permitted' in detail or 'Errno 1' in detail:
        return '系统权限限制，请检查网络和SSL证书配置'
    return '短信服务暂不可用，请检查阿里云短信配置后重试'


def check_sms_code(phone: str, code: str) -> Tuple[bool, str]:
    """
    校验短信验证码
    
    Args:
        phone: 手机号
        code: 用户输入的验证码
    
    Returns:
        tuple: (是否验证成功, 提示信息)
    """
    if not SMS_ENABLED:
        return False, "短信服务未配置，暂不可用"
    try:
        from alibabacloud_dypnsapi20170525 import models as dypns_models
        from alibabacloud_tea_util import models as util_models
        print(f"[SMS校验] 开始校验: phone={phone}, code={code}")
        
        client = AliyunSmsClient.get_client()
        
        # 构建请求 - 注意：CheckSmsVerifyCode可能不需要sign_name
        request = dypns_models.CheckSmsVerifyCodeRequest(
            phone_number=phone,
            verify_code=code
        )
        
        runtime = util_models.RuntimeOptions()
        
        # 校验验证码
        print(f"[SMS校验] 调用阿里云API...")
        response = client.check_sms_verify_code_with_options(request, runtime)
        
        print(f"[SMS校验] 响应状态码: {response.status_code}")
        print(f"[SMS校验] 响应body: {response.body}")
        
        # 检查响应
        if response.status_code == 200 and response.body:
            # 尝试获取验证结果
            body = response.body
            print(f"[SMS校验] body.code: {getattr(body, 'code', None)}")
            print(f"[SMS校验] body.message: {getattr(body, 'message', None)}")
            print(f"[SMS校验] body.model: {getattr(body, 'model', None)}")
            
            # 判断API调用是否成功
            if getattr(body, 'code', None) == 'OK':
                model = getattr(body, 'model', None)
                if model:
                    verify_result = getattr(model, 'verify_result', None)
                    print(f"[SMS校验] verify_result: {verify_result}")
                    
                    if verify_result == "PASS":
                        return True, "验证成功"
                    else:
                        print(f"[SMS校验] 验证失败: result={verify_result}")
                        return False, "验证码错误或已过期"
                else:
                    return False, "验证响应格式异常"
            else:
                error_code = getattr(body, 'code', 'UnknownError')
                error_message = getattr(body, 'message', '未知错误')
                print(f"[SMS校验] API返回错误: code={error_code}, message={error_message}")
                # 返回用户友好的错误信息
                if 'ValidateFail' in str(error_code) or '验证失败' in str(error_message):
                    return False, "验证码错误或已过期"
                return False, "验证码校验失败，请重新获取"
        else:
            return False, "验证码校验失败"
            
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"[SMS校验] 捕获异常: {error_type}: {error_msg}")
        
        # 打印完整堆栈
        import traceback
        print(f"[SMS校验] 错误堆栈:\n{traceback.format_exc()}")
        
        # 将阿里云错误转换为用户友好提示
        if 'VERIFY_CODE_ERROR' in error_msg or 'VerifyCodeError' in error_msg:
            message = '验证码错误'
        elif 'VERIFY_CODE_EXPIRED' in error_msg or 'VerifyCodeExpired' in error_msg:
            message = '验证码已过期，请重新获取'
        elif 'VERIFY_CODE_NOT_EXIST' in error_msg or 'VerifyCodeNotExist' in error_msg:
            message = '请先获取验证码'
        elif 'isv.PARAM_NOT_SUPPORT' in error_msg:
            message = '验证码参数错误'
        elif 'ValidateFail' in error_msg or '验证失败' in error_msg:
            message = '验证码错误或已过期'
        elif 'InvalidPhoneNumber' in error_msg or 'MOBILE_NUMBER_ILLEGAL' in error_msg:
            message = '手机号格式不正确'
        else:
            # 不暴露技术细节，返回通用错误信息
            message = '验证码校验失败，请重新获取验证码'
        
        return False, message


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆手机号）
    
    Args:
        phone: 手机号
    
    Returns:
        bool: 是否有效
    """
    if not phone:
        return False
    
    # 使用正则表达式验证手机号
    # 1开头，第二位3-9，共11位数字
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))
