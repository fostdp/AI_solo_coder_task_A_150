from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class AlertType(str, Enum):
    INCLINATION_EXCEEDED = "INCLINATION_EXCEEDED"
    MECHANISM_JAMMED = "MECHANISM_JAMMED"
    SENSOR_FAULT = "SENSOR_FAULT"


class AlertLevel(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Point3D(BaseModel):
    x: float
    y: float
    z: float


class Point2D(BaseModel):
    x: float
    y: float


class SensorData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: str = Field(..., description="设备唯一标识")
    crank_angle: float = Field(..., ge=0.0, le=360.0, description="曲柄转角 (0-360°)")
    leg_displacement: float = Field(..., description="腿足位移 (mm)")
    body_inclination: float = Field(..., description="机身倾角 (°)")
    ground_elevation: float = Field(..., description="地面起伏 (mm)")


class JansenParameters(BaseModel):
    crank_length: float = Field(default=150.0, description="曲柄长度 (mm)")
    rocker_length: float = Field(default=250.0, description="摇杆长度 (mm)")
    coupler_length: float = Field(default=300.0, description="连杆长度 (mm)")
    ground_link: float = Field(default=200.0, description="机架长度 (mm)")
    crank_speed: float = Field(default=30.0, description="曲柄转速 (°/s)")


class LegPosition(BaseModel):
    hip: Point3D
    knee: Point3D
    ankle: Point3D
    foot: Point3D


class LinkageState(BaseModel):
    crank_angle: float
    joint_positions: List[Point3D]
    leg_position: LegPosition
    foot_velocity: Point3D


class GaitAnalysisResult(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: str
    stride_length: float = Field(description="步幅 (mm)")
    cadence: float = Field(description="步频 (步/分钟)")
    support_phase: float = Field(description="支撑相比例 (%)")
    swing_phase: float = Field(description="摆动相比例 (%)")
    com_trajectory: List[Point3D] = Field(description="重心轨迹")
    zmp_trajectory: List[Point2D] = Field(description="零力矩点轨迹")
    stability_margin: float = Field(description="稳定裕度")
    linkage_state: Optional[LinkageState] = None


class TerrainPoint(BaseModel):
    x: float
    y: float
    elevation: float


class TerrainData(BaseModel):
    grid_size: int = Field(default=50, description="地形网格大小")
    resolution: float = Field(default=100.0, description="网格分辨率 (mm)")
    points: List[TerrainPoint] = Field(description="地形高程点")
    obstacles: List[dict] = Field(default_factory=list, description="障碍物列表")


class ObstacleAssessmentResult(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: str
    max_obstacle_height: float = Field(description="最大可越障高度 (mm)")
    max_slope_angle: float = Field(description="最大可爬坡角度 (°)")
    critical_inclination: float = Field(description="临界倾角 (°)")
    obstacle_pass_probability: float = Field(description="通过概率")
    recommended_speed: float = Field(description="推荐速度 (°/s)")
    risk_level: RiskLevel = Field(description="风险等级")
    terrain_analysis: dict = Field(description="地形分析结果")


class Alert(BaseModel):
    id: str
    timestamp: datetime
    type: AlertType
    level: AlertLevel
    message: str
    device_id: str
    sensor_data: SensorData
    acknowledged: bool = False


class DeviceInfo(BaseModel):
    device_id: str
    name: str
    status: str
    last_heartbeat: datetime
    parameters: JansenParameters


class WebSocketMessage(BaseModel):
    type: str
    payload: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GaitSimulationRequest(BaseModel):
    device_id: str
    parameters: JansenParameters
    crank_angle_range: Tuple[float, float] = Field(default=(0.0, 360.0))
    step_resolution: float = Field(default=1.0, description="计算步长 (°)")


class ObstacleAssessmentRequest(BaseModel):
    device_id: str
    parameters: JansenParameters
    terrain_data: TerrainData
    current_inclination: float = Field(default=0.0)
    current_speed: float = Field(default=30.0)
