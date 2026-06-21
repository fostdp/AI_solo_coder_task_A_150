from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from app.models.schemas import (
    JansenParameters,
    GaitAnalysisResult,
    GaitSimulationRequest,
    LinkageState,
    Point3D
)
from app.simulation.jansen_linkage import JansenLinkageSolver
from app.simulation.gait_engine import GaitEngine
from app.core.database import influx_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/simulation", tags=["仿真计算"])


@router.post("/gait", response_model=GaitAnalysisResult, summary="计算步态参数")
async def compute_gait_analysis(
    device_id: str = Query(..., description="设备ID"),
    parameters: JansenParameters = None,
    crank_angle: Optional[float] = Query(None, ge=0, le=360, description="曲柄转角"),
    body_inclination: float = Query(0.0, description="机身倾角")
):
    try:
        if parameters is None:
            parameters = JansenParameters()
        
        gait_engine = GaitEngine(parameters)
        result = gait_engine.compute_gait_analysis(
            device_id=device_id,
            crank_angle=crank_angle,
            body_inclination=body_inclination
        )
        
        await influx_db.write_gait_result(result)
        
        return result
    except Exception as e:
        logger.error(f"步态分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"步态分析失败: {str(e)}")


@router.post("/gait/full", summary="完整步态周期仿真")
async def compute_full_gait_simulation(request: GaitSimulationRequest):
    try:
        gait_engine = GaitEngine(request.parameters)
        results = gait_engine.compute_full_gait_simulation(request)
        return results
    except Exception as e:
        logger.error(f"完整步态仿真失败: {e}")
        raise HTTPException(status_code=500, detail=f"仿真失败: {str(e)}")


@router.get("/linkage", response_model=LinkageState, summary="计算连杆机构状态")
async def compute_linkage_state(
    crank_angle: float = Query(..., ge=0, le=360, description="曲柄转角"),
    crank_length: float = Query(150.0, description="曲柄长度"),
    rocker_length: float = Query(250.0, description="摇杆长度"),
    coupler_length: float = Query(300.0, description="连杆长度"),
    ground_link: float = Query(200.0, description="机架长度")
):
    try:
        params = JansenParameters(
            crank_length=crank_length,
            rocker_length=rocker_length,
            coupler_length=coupler_length,
            ground_link=ground_link
        )
        solver = JansenLinkageSolver(params)
        state = solver.get_linkage_state(crank_angle)
        return state
    except Exception as e:
        logger.error(f"连杆计算失败: {e}")
        raise HTTPException(status_code=500, detail=f"连杆计算失败: {str(e)}")


@router.get("/foot-trajectory", summary="生成足端轨迹")
async def generate_foot_trajectory(
    start_angle: float = Query(0.0, ge=0, le=360, description="起始转角"),
    end_angle: float = Query(360.0, ge=0, le=720, description="结束转角"),
    steps: int = Query(360, ge=36, le=3600, description="步数"),
    crank_length: float = Query(150.0, description="曲柄长度"),
    rocker_length: float = Query(250.0, description="摇杆长度"),
    coupler_length: float = Query(300.0, description="连杆长度"),
    ground_link: float = Query(200.0, description="机架长度")
):
    try:
        params = JansenParameters(
            crank_length=crank_length,
            rocker_length=rocker_length,
            coupler_length=coupler_length,
            ground_link=ground_link
        )
        solver = JansenLinkageSolver(params)
        trajectory = solver.generate_foot_trajectory(start_angle, end_angle, steps)
        
        return {
            "parameters": params.model_dump(),
            "trajectory": [p.model_dump() for p in trajectory],
            "bounds": {
                "min_x": min(p.x for p in trajectory),
                "max_x": max(p.x for p in trajectory),
                "min_y": min(p.y for p in trajectory),
                "max_y": max(p.y for p in trajectory),
                "stride_length": max(p.x for p in trajectory) - min(p.x for p in trajectory),
                "step_height": max(p.y for p in trajectory) - min(p.y for p in trajectory)
            }
        }
    except Exception as e:
        logger.error(f"轨迹生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"轨迹生成失败: {str(e)}")


@router.get("/link-angles", summary="计算各连杆角度")
async def get_link_angles(
    crank_angle: float = Query(..., ge=0, le=360, description="曲柄转角"),
    parameters: JansenParameters = None
):
    try:
        if parameters is None:
            parameters = JansenParameters()
        solver = JansenLinkageSolver(parameters)
        angles = solver.get_link_angles(crank_angle)
        return angles
    except Exception as e:
        logger.error(f"连杆角度计算失败: {e}")
        raise HTTPException(status_code=500, detail=f"角度计算失败: {str(e)}")


@router.get("/gait-phase", summary="获取步态相位信息")
async def get_gait_phase(
    crank_angle: float = Query(..., ge=0, le=360, description="曲柄转角"),
    num_phases: int = Query(8, ge=4, le=16, description="相位数量")
):
    try:
        params = JansenParameters()
        gait_engine = GaitEngine(params)
        phase_info = gait_engine.get_gait_phase(crank_angle, num_phases)
        return phase_info
    except Exception as e:
        logger.error(f"步态相位计算失败: {e}")
        raise HTTPException(status_code=500, detail=f"相位计算失败: {str(e)}")


@router.get("/gait-symmetry", summary="计算步态对称性")
async def compute_gait_symmetry(
    left_crank_offset: float = Query(180.0, description="左腿曲柄偏移"),
    crank_length: float = Query(150.0, description="曲柄长度"),
    rocker_length: float = Query(250.0, description="摇杆长度"),
    coupler_length: float = Query(300.0, description="连杆长度"),
    ground_link: float = Query(200.0, description="机架长度")
):
    try:
        params = JansenParameters(
            crank_length=crank_length,
            rocker_length=rocker_length,
            coupler_length=coupler_length,
            ground_link=ground_link
        )
        gait_engine = GaitEngine(params)
        
        left_result = gait_engine.compute_gait_analysis("left_leg", 0.0)
        right_result = gait_engine.compute_gait_analysis("right_leg", left_crank_offset)
        
        symmetry = gait_engine.compute_gait_symmetry(left_result, right_result)
        
        return {
            "left_leg": left_result.model_dump(),
            "right_leg": right_result.model_dump(),
            "symmetry_metrics": symmetry
        }
    except Exception as e:
        logger.error(f"对称性计算失败: {e}")
        raise HTTPException(status_code=500, detail=f"对称性计算失败: {str(e)}")


@router.get("/stability-prediction", summary="预测稳定性")
async def predict_stability(
    current_inclination: float = Query(0.0, description="当前倾角"),
    target_speed: float = Query(30.0, description="目标速度"),
    terrain_roughness: float = Query(0.0, description="地形粗糙度")
):
    try:
        params = JansenParameters()
        gait_engine = GaitEngine(params)
        prediction = gait_engine.predict_gait_stability(
            current_inclination=current_inclination,
            target_speed=target_speed,
            terrain_roughness=terrain_roughness
        )
        return prediction
    except Exception as e:
        logger.error(f"稳定性预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


@router.post("/optimize-parameters", summary="优化连杆参数")
async def optimize_parameters(
    target_stride_length: float = Query(None, description="目标步幅"),
    target_stability: float = Query(80.0, description="目标稳定性"),
    parameters: JansenParameters = None
):
    try:
        if parameters is None:
            parameters = JansenParameters()
        gait_engine = GaitEngine(parameters)
        optimized = gait_engine.optimize_gait_parameters(
            target_stride_length=target_stride_length,
            target_stability=target_stability
        )
        return {
            "original": parameters.model_dump(),
            "optimized": optimized.model_dump()
        }
    except Exception as e:
        logger.error(f"参数优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")
