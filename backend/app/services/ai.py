"""
火山方舟AI服务封装
"""
import requests
import json
from typing import List, Dict, Optional
from app.config import (
    VOLC_API_KEY,
    VOLC_API_BASE_URL,
    VOLC_MODEL,
    VOLC_MAX_TOKENS,
    VOLC_TEMPERATURE,
    VOLC_TIMEOUT
)


class VolcanoAIClient:
    """火山方舟AI客户端（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VolcanoAIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.api_key = VOLC_API_KEY
        self.base_url = VOLC_API_BASE_URL
        self.model = VOLC_MODEL
        self.max_tokens = VOLC_MAX_TOKENS
        self.temperature = VOLC_TEMPERATURE
        self.timeout = VOLC_TIMEOUT
        self._initialized = True
        
        if not self.api_key:
            print("[AI] 警告: 未配置VOLC_API_KEY")
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        disable_thinking: bool = True,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """构建请求体"""
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        # 关闭深度思考（节省token和时间）
        if disable_thinking:
            payload["thinking"] = {"type": "disabled"}
        
        # 可选参数
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        else:
            payload["max_tokens"] = self.max_tokens
            
        if temperature is not None:
            payload["temperature"] = temperature
        else:
            payload["temperature"] = self.temperature
        
        return payload
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        disable_thinking: bool = True,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        调用AI聊天接口
        
        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            disable_thinking: 是否禁用深度思考（默认True）
            max_tokens: 最大返回token数
            temperature: 温度参数（0-1，值越高越随机）
        
        Returns:
            {
                "success": bool,
                "content": str,  # AI回复内容
                "usage": dict,   # token使用情况
                "error": str     # 错误信息（如果有）
            }
        """
        print(f"[AI] 开始调用火山方舟AI: messages={len(messages)}条")
        
        if not self.api_key:
            return {
                "success": False,
                "content": "",
                "error": "未配置API Key"
            }
        
        try:
            url = f"{self.base_url}/chat/completions"
            headers = self._build_headers()
            payload = self._build_payload(
                messages=messages,
                disable_thinking=disable_thinking,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            print(f"[AI] 请求URL: {url}")
            print(f"[AI] 请求参数: model={self.model}, max_tokens={payload.get('max_tokens')}, temperature={payload.get('temperature')}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            print(f"[AI] 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 提取回复内容
                choices = result.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    usage = result.get("usage", {})
                    
                    print(f"[AI] 调用成功: content长度={len(content)}, usage={usage}")
                    
                    return {
                        "success": True,
                        "content": content,
                        "usage": usage
                    }
                else:
                    print(f"[AI] 响应格式异常: {result}")
                    return {
                        "success": False,
                        "content": "",
                        "error": "AI响应格式异常"
                    }
            else:
                error_msg = response.text
                print(f"[AI] API调用失败: {error_msg}")
                return {
                    "success": False,
                    "content": "",
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            print(f"[AI] 请求超时")
            return {
                "success": False,
                "content": "",
                "error": "请求超时，请稍后重试"
            }
        except Exception as e:
            print(f"[AI] 调用异常: {e}")
            return {
                "success": False,
                "content": "",
                "error": f"调用异常: {str(e)}"
            }
    
    def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> Dict:
        """
        简单对话（单轮）
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词（可选）
        
        Returns:
            AI回复结果
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.chat(messages)


# 导出单例实例
ai_client = VolcanoAIClient()


def chat_with_ai(
    messages: List[Dict[str, str]],
    disable_thinking: bool = True,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> Dict:
    """
    便捷函数：调用AI聊天
    """
    return ai_client.chat(
        messages=messages,
        disable_thinking=disable_thinking,
        max_tokens=max_tokens,
        temperature=temperature
    )


def simple_chat(user_message: str, system_prompt: Optional[str] = None) -> Dict:
    """
    便捷函数：简单对话
    """
    return ai_client.simple_chat(user_message, system_prompt)

