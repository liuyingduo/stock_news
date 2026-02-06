from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration"""

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "stock_news"

    # Zhipu AI
    zhipu_api_key: str = ""
    ai_model: str = "glm-4.7-flash"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: List[str] = ["*"]

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # WeChat Pay v3
    wechat_mchid: str = ""
    wechat_appid: str = ""
    wechat_serial_no: str = ""
    wechat_private_key_path: str = ""
    wechat_api_v3_key: str = ""
    wechat_notify_url: str = ""

    # Alipay
    alipay_app_id: str = ""
    alipay_private_key_path: str = ""
    alipay_public_key_path: str = ""
    alipay_notify_url: str = ""

    # WeChat Open Platform (QR Login)
    wechat_open_appid: str = ""
    wechat_open_secret: str = ""
    wechat_open_redirect_uri: str = ""

    # Tencent SMS
    tencent_sms_secret_id: str = ""
    tencent_sms_secret_key: str = ""
    tencent_sms_app_id: str = ""
    tencent_sms_sign_name: str = ""
    tencent_sms_template_id: str = ""
    tencent_sms_country_code: str = "+86"

    # Frontend
    frontend_base_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

