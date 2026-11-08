"""
火山方舟AI服务封装
提供统一的AI调用接口
"""
import requests
from typing import List, Dict, Optional, Any
from app.config import AI_ENABLED, VOLCENGINE_ARK_API_KEY, VOLCENGINE_ARK_MODEL, VOLCENGINE_ARK_BASE_URL


class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.api_key = VOLCENGINE_ARK_API_KEY
        self.model = VOLCENGINE_ARK_MODEL
        self.base_url = VOLCENGINE_ARK_BASE_URL
        self.chat_endpoint = f"{self.base_url}/chat/completions"
    
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送AI请求
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            API响应结果
        """
        if not AI_ENABLED:
            raise ValueError("AI service disabled; set AI_ENABLED=true to opt in")
        if not self.api_key:
            raise ValueError("VOLCENGINE_ARK_API_KEY 未配置，请在 .env 文件中设置")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "thinking": {"type": "disabled"},  # 关闭深度思考
            **kwargs
        }
        
        try:
            response = requests.post(
                self.chat_endpoint,
                headers=headers,
                json=payload,
                timeout=(10, 60)  # 连接超时10秒，读取超时60秒
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"AI API请求失败: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                    error_msg += f"\n响应内容: {error_detail}"
                except:
                    pass
            raise RuntimeError(error_msg) from e
    
    def chat(self, user_message: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        简单的对话接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
        
        Returns:
            AI回复内容
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
        
        result = self._make_request(messages, **kwargs)
        
        # 提取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            if "content" in message:
                return message["content"]
            else:
                raise ValueError(f"AI响应中缺少content字段: {result}")
        else:
            raise ValueError(f"AI响应格式异常，未找到choices: {result}")
    
    def chat_with_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        带历史记录的对话接口
        
        Args:
            messages: 完整的消息历史，格式：
                [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    {"role": "user", "content": "..."}
                ]
            **kwargs: 其他参数
        
        Returns:
            AI回复内容
        """
        result = self._make_request(messages, **kwargs)
        
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            if "content" in message:
                return message["content"]
            else:
                raise ValueError(f"AI响应中缺少content字段: {result}")
        else:
            raise ValueError(f"AI响应格式异常，未找到choices: {result}")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        文本生成接口
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            temperature: 温度参数（0-1，越高越随机）
        
        Returns:
            生成的文本
        """
        return self.chat(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )


# 创建全局实例
ai_service = AIService()


def get_ai_service() -> AIService:
    """获取AI服务实例"""
    return ai_service

