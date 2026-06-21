from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from app.core.config import settings
from app.core.database import influx_db, redis_db
from app.api.sensor import router as sensor_router
from app.api.simulation import router as simulation_router
from app.api.analysis import router as analysis_router
from app.api.alert import router as alert_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"启动 {settings.app_name} 服务...")
    logger.info(f"环境: {settings.app_env}")
    logger.info(f"InfluxDB URL: {settings.influxdb_url}")
    logger.info(f"服务端口: {settings.app_port}")
    
    yield
    
    logger.info("正在关闭服务...")
    influx_db.close()
    await redis_db.close()
    logger.info("服务已关闭")


app = FastAPI(
    title=settings.app_name,
    description="古代木牛流马行走机构仿真与越障能力分析系统 - API接口文档",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor_router)
app.include_router(simulation_router)
app.include_router(analysis_router)
app.include_router(alert_router)


@app.get("/", summary="根路径")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "endpoints": {
            "sensors": "/api/sensors",
            "simulation": "/api/simulation",
            "analysis": "/api/analysis",
            "alerts": "/api/alerts"
        }
    }


@app.get("/health", summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "influxdb": "connected" if influx_db.client else "disconnected",
            "redis": "connected" if redis_db.redis else "disconnected"
        }
    }


@app.get("/api/info", summary="系统信息")
async def get_system_info():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "features": [
            "Jansen连杆理论求解",
            "多体动力学仿真",
            "步态分析与优化",
            "地形识别与越障评估",
            "稳定性分析",
            "WebSocket实时告警",
            "Modbus RTU数据采集",
            "InfluxDB时序存储"
        ],
        "alert_thresholds": {
            "inclination": settings.alert_inclination_threshold,
            "mechanism_jam": settings.alert_jammed_threshold
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development"
    )
