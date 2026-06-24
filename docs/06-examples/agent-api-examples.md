# xiaomiaoAgent API 调用示例

**版本**: v1.0  
**更新日期**: 2026-06-24

本文档提供 xiaomiaoAgent OpenAI 兼容 API 的调用示例。

---

## 📋 目录

1. [API 基础信息](#api-基础信息)
2. [Python 调用示例](#python-调用示例)
3. [JavaScript/TypeScript 调用示例](#javascripttypescript-调用示例)
4. [cURL 调用示例](#curl-调用示例)
5. [流式响应](#流式响应)
6. [工具调用](#工具调用)
7. [错误处理](#错误处理)

---

## API 基础信息

### 服务地址
```
http://127.0.0.1:8900/v1/chat/completions
```

### 认证
本地部署无需 API Key，但需要确保服务已启动。

### 启动服务
```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python -m xiaomiao_agent serve --config xiaomiaoAgent\.nanobot\config.json
```

### 健康检查
```bash
curl http://127.0.0.1:8900/health
```

---

## Python 调用示例

### 1. 使用 OpenAI SDK

```python
from openai import OpenAI

# 创建客户端
client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="not-needed"  # 本地部署不需要真实 key
)

# 发送聊天请求
response = client.chat.completions.create(
    model="deepseek-v4-flash",  # 使用配置文件中的模型
    messages=[
        {"role": "system", "content": "你是小喵，一个可爱的AI助手。"},
        {"role": "user", "content": "你好，介绍一下你自己"}
    ],
    temperature=0.7,
    max_tokens=1000
)

# 获取回复
print(response.choices[0].message.content)
```

### 2. 使用 requests 库

```python
import requests
import json

url = "http://127.0.0.1:8900/v1/chat/completions"

payload = {
    "model": "deepseek-v4-flash",
    "messages": [
        {"role": "system", "content": "你是小喵，一个可爱的AI助手。"},
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": False
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"错误: {response.status_code} - {response.text}")
```

### 3. 多轮对话

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="not-needed"
)

# 对话历史
messages = [
    {"role": "system", "content": "你是小喵，一个可爱的AI助手。"}
]

def chat(user_input):
    # 添加用户消息
    messages.append({"role": "user", "content": user_input})
    
    # 发送请求
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        temperature=0.7
    )
    
    # 获取助手回复
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

# 使用示例
print(chat("你好"))
print(chat("我叫小明"))
print(chat("你还记得我的名字吗？"))
```

---

## JavaScript/TypeScript 调用示例

### 1. 使用 OpenAI SDK (Node.js)

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://127.0.0.1:8900/v1',
  apiKey: 'not-needed'
});

async function chat(message: string) {
  const response = await client.chat.completions.create({
    model: 'deepseek-v4-flash',
    messages: [
      { role: 'system', content: '你是小喵，一个可爱的AI助手。' },
      { role: 'user', content: message }
    ],
    temperature: 0.7,
    max_tokens: 1000
  });

  return response.choices[0].message.content;
}

// 使用示例
chat('你好').then(reply => console.log(reply));
```

### 2. 使用 fetch API (浏览器)

```typescript
async function chatWithXiaomiao(message: string): Promise<string> {
  const response = await fetch('http://127.0.0.1:8900/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'deepseek-v4-flash',
      messages: [
        { role: 'system', content: '你是小喵，一个可爱的AI助手。' },
        { role: 'user', content: message }
      ],
      temperature: 0.7,
      max_tokens: 1000,
      stream: false
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

// 使用示例
chatWithXiaomiao('你好')
  .then(reply => console.log(reply))
  .catch(error => console.error('错误:', error));
```

### 3. Vue 3 组件示例

```vue
<script setup lang="ts">
import { ref } from 'vue';

const userInput = ref('');
const messages = ref<Array<{ role: string; content: string }>>([]);
const isLoading = ref(false);

async function sendMessage() {
  if (!userInput.value.trim()) return;

  const newMessage = userInput.value;
  userInput.value = '';
  isLoading.value = true;

  // 添加用户消息
  messages.value.push({ role: 'user', content: newMessage });

  try {
    const response = await fetch('http://127.0.0.1:8900/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'deepseek-v4-flash',
        messages: [
          { role: 'system', content: '你是小喵，一个可爱的AI助手。' },
          ...messages.value
        ],
        temperature: 0.7
      })
    });

    const data = await response.json();
    const reply = data.choices[0].message.content;

    // 添加助手回复
    messages.value.push({ role: 'assistant', content: reply });
  } catch (error) {
    console.error('API 调用失败:', error);
    messages.value.push({ role: 'assistant', content: '抱歉，出错了' });
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="chat-container">
    <div v-for="msg in messages" :key="msg" class="message">
      <div :class="msg.role">{{ msg.content }}</div>
    </div>
    <input 
      v-model="userInput" 
      @keyup.enter="sendMessage"
      :disabled="isLoading"
      placeholder="输入消息..."
    />
    <button @click="sendMessage" :disabled="isLoading">
      {{ isLoading ? '发送中...' : '发送' }}
    </button>
  </div>
</template>
```

---

## cURL 调用示例

### 1. 基本调用

```bash
curl -X POST http://127.0.0.1:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {"role": "system", "content": "你是小喵，一个可爱的AI助手。"},
      {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 2. Windows PowerShell

```powershell
$body = @{
    model = "deepseek-v4-flash"
    messages = @(
        @{role = "system"; content = "你是小喵，一个可爱的AI助手。"}
        @{role = "user"; content = "你好"}
    )
    temperature = 0.7
    max_tokens = 1000
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8900/v1/chat/completions" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

## 流式响应

### Python 流式调用

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="not-needed"
)

# 流式请求
stream = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是小喵，一个可爱的AI助手。"},
        {"role": "user", "content": "讲一个故事"}
    ],
    stream=True
)

# 逐块接收并打印
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

### JavaScript 流式调用

```typescript
async function streamChat(message: string) {
  const response = await fetch('http://127.0.0.1:8900/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'deepseek-v4-flash',
      messages: [
        { role: 'system', content: '你是小喵，一个可爱的AI助手。' },
        { role: 'user', content: message }
      ],
      stream: true
    })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.trim());

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') continue;

        try {
          const parsed = JSON.parse(data);
          const content = parsed.choices[0]?.delta?.content;
          if (content) {
            process.stdout.write(content);
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    }
  }
}
```

---

## 工具调用

### Python 工具调用示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="not-needed"
)

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 发送请求
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "user", "content": "北京今天天气怎么样？"}
    ],
    tools=tools,
    tool_choice="auto"
)

# 检查是否需要调用工具
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"需要调用工具: {tool_call.function.name}")
    print(f"参数: {tool_call.function.arguments}")
```

---

## 错误处理

### 完整的错误处理示例

```python
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chat_with_retry(message: str, max_retries: int = 3):
    client = OpenAI(
        base_url="http://127.0.0.1:8900/v1",
        api_key="not-needed"
    )

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "你是小喵，一个可爱的AI助手。"},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                timeout=30.0  # 30 秒超时
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"第 {attempt + 1} 次尝试失败: {e}")
            
            if attempt == max_retries - 1:
                logger.error("达到最大重试次数，放弃")
                raise
            
            # 等待后重试
            import time
            time.sleep(2 ** attempt)  # 指数退避

# 使用示例
try:
    reply = chat_with_retry("你好")
    print(reply)
except Exception as e:
    print(f"聊天失败: {e}")
```

### 常见错误处理

```python
from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError

client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="not-needed"
)

try:
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": "你好"}]
    )
    print(response.choices[0].message.content)

except APIConnectionError:
    print("❌ 无法连接到 API 服务")
    print("请检查：")
    print("1. xiaomiaoAgent 服务是否启动")
    print("2. 端口 8900 是否正确")
    print("3. 防火墙设置")

except APITimeoutError:
    print("❌ 请求超时")
    print("服务可能负载过高或响应缓慢")

except RateLimitError:
    print("❌ 请求频率超限")
    print("请稍后再试")

except Exception as e:
    print(f"❌ 未知错误: {e}")
```

---

## 完整应用示例

### 简单的聊天 CLI

```python
from openai import OpenAI
import sys

def main():
    client = OpenAI(
        base_url="http://127.0.0.1:8900/v1",
        api_key="not-needed"
    )

    messages = [
        {"role": "system", "content": "你是小喵，一个可爱的AI助手。"}
    ]

    print("小喵聊天 CLI (输入 'exit' 退出)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            if not user_input:
                continue

            # 添加用户消息
            messages.append({"role": "user", "content": user_input})

            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                temperature=0.7,
                stream=True
            )

            # 流式输出
            print("小喵: ", end='', flush=True)
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content

            # 添加助手消息到历史
            messages.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            print("\n\n再见！")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    main()
```

---

## 性能优化建议

### 1. 连接复用

```python
# ✅ 推荐：复用客户端
client = OpenAI(base_url="http://127.0.0.1:8900/v1", api_key="not-needed")

def chat(message):
    return client.chat.completions.create(...)

# ❌ 不推荐：每次创建新客户端
def chat(message):
    client = OpenAI(...)  # 每次调用都创建
    return client.chat.completions.create(...)
```

### 2. 批量请求

```python
import asyncio
from openai import AsyncOpenAI

async def batch_chat(messages_list):
    client = AsyncOpenAI(
        base_url="http://127.0.0.1:8900/v1",
        api_key="not-needed"
    )

    tasks = [
        client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": msg}]
        )
        for msg in messages_list
    ]

    responses = await asyncio.gather(*tasks)
    return [r.choices[0].message.content for r in responses]

# 使用
messages = ["你好", "今天天气", "讲个笑话"]
replies = asyncio.run(batch_chat(messages))
```

---

## 📚 相关文档

- [xiaomiaoAgent 文档](../03-subsystems/xiaomiaoAgent/README.md) - Agent 框架详解
- [配置示例](config-examples.md) - 配置文件示例
- [故障排查](../01-configuration/troubleshooting.md) - 问题解决

---

**更新日志**:
- v1.0 (2026-06-24) - 初始版本，包含 Python、JavaScript、cURL 示例

**需要帮助？** 查看 [故障排查文档](../01-configuration/troubleshooting.md) 或提 Issue。
