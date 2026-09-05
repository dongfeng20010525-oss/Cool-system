# 制冷系统仿真 MVP

这是一个基于 Streamlit 和 CoolProp 的单级稳态蒸汽压缩制冷循环 MVP。用户输入基础运行参数后，可以查看制冷量、压缩机功率、COP、四个状态点和 P-h 循环图。

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

项目使用 CoolProp 进行制冷剂物性计算，当前支持 R134a、R410A 和 R32。结果用于早期方案估算，不替代完整设备选型或实验验证。

## 演示流程

1. 在左侧选择制冷剂并调整运行参数。
2. 点击“运行仿真”。
3. 查看物性计算得到的制冷量、压缩机功率和 COP。
4. 查看四个状态点及 P-h 循环图。
5. 将冷凝温度调低到不高于蒸发温度，点击运行，查看错误提示流程。
