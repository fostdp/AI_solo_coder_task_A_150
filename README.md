# 古代木牛流马行走机构仿真与越障能力分析系统

一套用于三国时期木牛流马复原研究的全栈仿真分析系统，基于Jansen连杆理论和多体动力学，实现行走机构仿真、越障能力评估和实时告警功能。

## 系统架构

```
┌─────────────────┐     Modbus RTU     ┌─────────────────┐
│  传感器模拟器   │ ──────────────────> │  数据采集服务   │
└─────────────────┘                    └────────┬────────┘
                                                  │
                                                  ▼
┌─────────────────┐   WebSocket/HTTP   ┌─────────────────┐
│   前端展示层    │ <───────────────── │  FastAPI后端    │
│  (React+Three.js)│                   │  (Python)       │
└─────────────────┘                    └────────┬────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │   InfluxDB      │
                                        │  (时序数据库)   │
                                        └─────────────────┘
```

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: InfluxDB 2.x (时序数据存储)
- **缓存**: Redis
- **通信协议**: Modbus RTU, WebSocket
- **科学计算**: NumPy, SciPy

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **3D渲染**: Three.js + React Three Fiber
- **UI组件**: Ant Design
- **图表**: ECharts
- **状态管理**: Zustand

### 部署
- Docker Compose
- 容器化部署

## 项目结构

```
.
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── sensor.py       # 传感器数据接口
│   │   │   ├── simulation.py   # 仿真计算接口
│   │   │   ├── analysis.py     # 分析评估接口
│   │   │   └── alert.py        # 告警管理接口
│   │   ├── core/           # 核心模块
│   │   │   ├── config.py       # 配置管理
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── websocket.py    # WebSocket管理
│   │   ├── models/         # 数据模型
│   │   │   └── schemas.py      # Pydantic模型
│   │   ├── simulation/     # 仿真计算
│   │   │   ├── jansen_linkage.py   # Jansen连杆求解
│   │   │   ├── multibody_dynamics.py # 多体动力学
│   │   │   └── gait_engine.py      # 步态引擎
│   │   ├── analysis/       # 分析评估
│   │   │   ├── terrain_recognition.py # 地形识别
│   │   │   ├── stability_analysis.py  # 稳定性分析
│   │   │   └── obstacle_analysis.py   # 越障能力分析
│   │   └── services/       # 业务服务
│   │       ├── modbus_client.py  # Modbus客户端
│   │       ├── data_processor.py # 数据处理器
│   │       └── alert_service.py  # 告警服务
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python依赖
│   ├── .env                # 环境变量
│   └── Dockerfile
├── frontend/                # React前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   │   ├── WoodOxScene.tsx    # 3D场景
│   │   │   ├── WoodOxBody.tsx     # 木牛流马主体
│   │   │   ├── JansenLinkage.tsx  # Jansen连杆
│   │   │   ├── SensorDataPanel.tsx # 传感器数据面板
│   │   │   ├── ControlPanel.tsx    # 控制面板
│   │   │   └── AlertPanel.tsx      # 告警面板
│   │   ├── hooks/          # 自定义Hooks
│   │   │   └── useWebSocket.ts    # WebSocket Hook
│   │   ├── store/          # 状态管理
│   │   │   └── useAppStore.ts     # Zustand Store
│   │   ├── types/          # 类型定义
│   │   ├── utils/          # 工具函数
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── tsconfig.json
├── influxdb/                # InfluxDB配置
│   ├── init_db.py          # 初始化脚本
│   ├── scripts/
│   │   └── setup.sh        # Shell初始化脚本
│   └── flux_queries.md     # Flux查询示例
├── simulator/               # 传感器模拟器
│   ├── modbus_sensor_simulator.py  # Modbus传感器模拟器
│   ├── modbus_data_collector.py    # 数据采集服务
│   ├── devices_config.json         # 设备配置
│   └── requirements.txt
├── docker-compose.yml       # Docker编排
├── test_core_modules.py     # 核心模块测试
└── README.md
```

## 核心功能

### 1. 行走机构仿真
- **Jansen连杆理论**: 精确求解腿足机构运动学
- **多体动力学**: 计算重心、零力矩点(ZMP)、关节力矩
- **步态分析**: 步幅、步频、支撑相/摆动相比例、步态对称性
- **足端轨迹**: 生成完整步态周期的足端运动轨迹

### 2. 越障能力分析
- **地形识别**: 地形分类、粗糙度计算、障碍物检测
- **稳定性分析**: 静态/动态稳定性、临界倾角、稳定椭球
- **越障评估**: 最大可越障高度、最大爬坡角度、通过概率
- **越障仿真**: 模拟障碍物通过过程，计算间隙和应力

### 3. 数据采集与存储
- **Modbus RTU**: 模拟传感器数据采集
- **InfluxDB**: 时序数据高效存储
- **数据处理**: 派生指标计算、数据质量评估

### 4. 告警系统
- **倾角告警**: 机身倾角超限时触发
- **卡死告警**: 机构运动异常时触发
- **WebSocket推送**: 实时告警通知
- **连续确认机制**: 需连续3次超阈值才告警，避免误报

### 5. 3D可视化
- **木牛流马模型**: 古风设计三维模型
- **连杆动画**: Jansen连杆机构实时运动
- **地形生成**: 可配置地形和障碍物
- **轨迹展示**: 足端运动轨迹可视化

## 快速开始

### 方式一：Docker Compose (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

服务启动后访问:
- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- InfluxDB: http://localhost:8086

### 方式二：本地开发

#### 1. 启动InfluxDB和Redis

```bash
docker-compose up -d influxdb redis
```

#### 2. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

#### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 启动传感器模拟器

```bash
cd simulator

# 安装依赖
pip install -r requirements.txt

# 启动模拟器（正常模式）
python modbus_sensor_simulator.py --mode normal
```

## API接口

### 传感器数据
- `GET /api/sensors/realtime` - 获取实时传感器数据
- `GET /api/sensors/history` - 获取历史传感器数据
- `POST /api/sensors/ingest` - 上报传感器数据
- `GET /api/sensors/statistics` - 获取统计数据

### 仿真计算
- `POST /api/simulation/gait` - 计算步态参数
- `GET /api/simulation/linkage` - 获取连杆状态
- `GET /api/simulation/foot-trajectory` - 获取足端轨迹
- `GET /api/simulation/gait-phase` - 获取步态相位

### 分析评估
- `POST /api/analysis/obstacle` - 越障能力评估
- `POST /api/analysis/terrain` - 地形分析
- `POST /api/analysis/stability/static` - 静态稳定性分析

### 告警管理
- `GET /api/alerts/current` - 获取当前活动告警
- `GET /api/alerts/history` - 获取告警历史
- `PUT /api/alerts/{id}/acknowledge` - 确认告警
- `WebSocket /api/alerts/ws` - 实时告警推送

## 核心算法

### Jansen连杆理论
基于余弦定理求解四杆机构封闭解，计算关节位置和足端轨迹。

```python
cos_phi = (b² + dist² - c²) / (2 * b * dist)
phi = arccos(clamp(cos_phi, -1, 1))
```

### 零力矩点(ZMP)
通过重心位置和作用力矩计算ZMP，评估行走稳定性。

### 稳定性裕度
计算ZMP到支撑多边形各边的最小距离，判断稳定性等级：
- excellent: >50mm
- good: 30-50mm
- marginal: 10-30mm
- poor: 0-10mm
- unstable: <0mm

## 配置说明

### 后端环境变量 (.env)
```env
APP_NAME=木牛流马仿真系统
APP_ENV=development
APP_PORT=8000

INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=wood-ox-admin-token
INFLUXDB_ORG=wood-ox-research
INFLUXDB_BUCKET=sensor_raw

ALERT_INCLINATION_THRESHOLD=15.0
ALERT_JAMMED_THRESHOLD=5.0
```

### Jansen连杆参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| crank_length | 150mm | 曲柄长度 |
| rocker_length | 250mm | 摇杆长度 |
| coupler_length | 300mm | 连杆长度 |
| ground_link | 200mm | 机架长度 |
| crank_speed | 30°/s | 曲柄转速 |

## 测试

### 核心模块测试
```bash
python test_core_modules.py
```

测试内容包括：
- Jansen连杆求解
- 多体动力学计算
- 步态参数分析
- 稳定性分析
- 地形识别
- 越障能力评估

## 开发说明

### 添加新的告警类型
1. 在 `app/models/schemas.py` 的 `AlertType` 枚举中添加新类型
2. 在 `app/services/alert_service.py` 中实现检测逻辑
3. 在前端 `src/types/index.ts` 中同步类型定义

### 添加新的仿真参数
1. 在 `JansenParameters` 模型中添加字段
2. 在 `JansenLinkageSolver` 中使用新参数
3. 在前端控制面板中添加调节控件

## 许可证

MIT License

## 参考文献

- Jansen, T. (2007). The Fantastic Apollowalker.
- 陈清泉. (2006). 多体系统动力学.
- 诸葛亮. (三国时期). 木牛流马制法 [史料记载].
