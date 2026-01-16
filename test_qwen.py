import dashscope
dashscope.api_key = "sk-352ac2c447984745ad305c07ee3d169a"  # ←←← 在这里粘贴你的 sk- 开头的 Key！

response = dashscope.Generation.call(
    model="qwen-max",
    prompt="你好，请用一句话介绍你自己。"
)
print(response.output.text)