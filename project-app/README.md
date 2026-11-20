# “桩”尽其用 · 项目初始框架

Streamlit 四页原型，对应当前项目四个重点：

1. **价格地图**：平台价、实付价、价格偏差、全成本、假空闲率；地图 + 差价榜 + 清单。
2. **站点账单**：电网、运营商、证据等级；电费/服务费/停车费拆解；平台价 vs 实付价。
3. **治理沙盘**：免费宽限、超时占用费、封顶、预约；等待/假空闲/有效供给对比。
4. **反馈中心**：价格不符、占位、坏桩、排队；表单 + 列表（会话内演示）。

## 运行

```powershell
cd "D:\学校文件\数据要素大赛\project-app"
C:\电脑应用\Python\.venv\Scripts\streamlit.exe run app.py
```

默认打开 http://localhost:8501。

## 文件结构

```
project-app/
├── app.py
├── data/
│   └── stations.csv        # 20 个长沙示例站点
├── .streamlit/
│   └── config.toml         # 主题与 headless
└── README.md
```

## 数据字段

| 字段 | 说明 |
|---|---|
| station_id / station_name | 站点 ID / 名称 |
| district | 区 |
| grid_company | 电网：国网湖南 / 园区增量配电网 / 地方电网（示例） |
| operator | 运营商 |
| lng / lat | 经纬度 |
| piles | 桩数 |
| price_elec / price_service | 电费、服务费（元/度） |
| price_parking | 停车费（元/小时） |
| platform_price | 平台展示总价（元/度） |
| field_price | 现场实付总价（元/度） |
| occupancy | 占用率 |
| queue | 平均排队（分钟） |
| fake_idle | 假空闲率（0—1） |
| feedback_count | 反馈条数 |
| evidence | 证据等级 A/B/C |

## 说明

- 示例数据是**合成数据**，只用于跑通页面；真实数据接 `data/stations.csv` 或侧边栏上传。
- 治理沙盘用简化公式（等待、假空闲随费率下降），不是实证模型；后续替换为排队/仿真。
- 反馈只存在 `st.session_state`，刷新会回到示例；接后端后可持久化。
- 下一步：接入真实价格审计表、20—30 站实地核查、电网电价政策库、用户反馈审核。
