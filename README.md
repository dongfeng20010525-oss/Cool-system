# 制冷系统仿真 Demo

这是一个用于验证产品界面和操作流程的 Streamlit 原型。当前版本使用确定性的模拟数据，不调用 CoolProp，也不实现真实后端仿真。

## 启动

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

启动后在浏览器打开 Streamlit 输出的本地地址。

## 测试

```powershell
pytest
```

## 演示流程

1. 在左侧选择制冷剂并调整运行参数。
2. 点击“运行仿真”。
3. 查看制冷量、压缩机功率和 COP。
4. 查看四个状态点及 P-h 循环图。
5. 将冷凝温度调低到不高于蒸发温度，点击运行，查看错误提示流程。

