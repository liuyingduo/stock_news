from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import events, sectors, stocks, dashboard, auth, payments
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接 MongoDB
    await connect_to_mongo()
    yield
    # 关闭时断开 MongoDB 连接
    await close_mongo_connection()

app = FastAPI(
    title="Stock News Analysis API",
    description="金融事件获取与分析系统 API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(sectors.router)
app.include_router(stocks.router)
app.include_router(dashboard.router)
app.include_router(payments.router)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Stock News Analysis API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
