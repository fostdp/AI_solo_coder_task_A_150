export interface Point3D {
  x: number
  y: number
  z: number
}

export interface Point2D {
  x: number
  y: number
}

export interface SensorData {
  timestamp: string
  device_id: string
  crank_angle: number
  leg_displacement: number
  body_inclination: number
  ground_elevation: number
}

export interface JansenParameters {
  crank_length: number
  rocker_length: number
  coupler_length: number
  ground_link: number
  crank_speed: number
  body_mass: number
  leg_mass: number
}

export interface LinkageState {
  crank_angle: number
  joints: Record<string, Point3D>
  foot_position: Point3D
  link_angles: Record<string, number>
  is_singular: boolean
}

export interface GaitAnalysisResult {
  device_id: string
  timestamp: string
  stride_length: number
  cadence: number
  support_phase: number
  swing_phase: number
  stability_margin: number
  gait_symmetry: number
  com_trajectory: Point3D[]
  zmp_trajectory: Point2D[]
  foot_trajectory: Point3D[]
  parameters: JansenParameters
}

export interface TerrainPoint {
  x: number
  y: number
  elevation: number
}

export interface TerrainData {
  grid_size: number
  resolution: number
  points: TerrainPoint[]
}

export interface ObstacleAssessmentRequest {
  device_id: string
  terrain_data: TerrainData
  current_inclination: number
  current_speed: number
  parameters: JansenParameters
}

export interface ObstacleAssessmentResult {
  device_id: string
  timestamp: string
  max_obstacle_height: number
  max_slope_angle: number
  critical_inclination: number
  obstacle_pass_probability: number
  recommended_speed: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  terrain_analysis: Record<string, number>
  parameters: JansenParameters
}

export enum AlertType {
  INCLINATION_EXCEEDED = 'INCLINATION_EXCEEDED',
  MECHANISM_JAMMED = 'MECHANISM_JAMMED',
  SENSOR_FAULT = 'SENSOR_FAULT'
}

export enum AlertLevel {
  INFO = 'INFO',
  WARNING = 'WARNING',
  CRITICAL = 'CRITICAL'
}

export interface Alert {
  id: string
  timestamp: string
  type: AlertType
  level: AlertLevel
  message: string
  device_id: string
  sensor_data: SensorData
  acknowledged: boolean
}

export interface WebSocketMessage {
  type: string
  payload: Record<string, any>
}

export interface StabilityAnalysisResult {
  static_stability: number
  dynamic_stability: number
  critical_inclination: number
  stability_margin: number
  com_position: Point3D
  zmp_position: Point2D
  support_polygon: Point2D[]
  risk_assessment: string
}

export interface DerivedMetrics {
  angular_velocity: number
  leg_velocity: number
  inclination_rate: number
  ground_gradient: number
  energy_consumption: number
  power_efficiency: number
}

export interface DataQuality {
  score: number
  issues: string[]
  validity: Record<string, boolean>
}
