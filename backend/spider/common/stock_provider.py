
import requests
import pandas as pd
from typing import Optional

class StockProvider:
    """股票数据提供者，封装所有底层数据获取逻辑"""
    
    @staticmethod
    def get_stock_zh_a_spot_em() -> pd.DataFrame:
        """
        自定义获取A股实时行情，替代 ak.stock_zh_a_spot_em
        解决官方接口被封锁或超时的问题
        """
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
            "Referer": "https://quote.eastmoney.com/center/gridlist.html",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Cookie": "qgqp_b_id=8bba8dfcac89e349ea5f7c6dd0c77419; st_nvi=FFKmX_1VRW5fJAALM8UEE6831; nid18=012843587801ee6a9d5e7da8627790e9; nid18_create_time=1765721048636; gviem=v-31g9WxJVxPUTdo_f7PF1762; gviem_create_time=1765721048636; emshistory=%5B%22%E7%BE%8E%E7%9A%84%E9%9B%86%E5%9B%A2%22%2C%22%E6%AD%8C%E5%B0%94%E8%82%A1%E4%BB%BD%22%2C%22%E7%AB%8B%E8%AE%AF%E7%B2%BE%E5%AF%86%22%2C%22%E6%8C%AF%E5%BE%B7%E5%8C%BB%E8%8D%AF%22%2C%22%E4%B8%9A%E7%BB%A9%E9%A2%84%E5%91%8A%22%2C%22002716%22%2C%22002346%22%2C%22002912%22%2C%22002395%22%2C%22002246%22%5D; fullscreengg=1; fullscreengg2=1; st_si=91285665801550; st_asi=delete; st_pvi=36075007809780; st_sp=2024-12-31%2015%3A19%3A44; st_inirUrl=https%3A%2F%2Fjiutian.10086.cn%2F; st_sn=2; st_psi=20260129215048475-113200301321-3244421071"
        }
        
        # Optimize fields to match user provided usage + what we need
        fields = "f12,f13,f14,f1,f2,f4,f3,f152,f5,f6,f7,f15,f18,f16,f17,f10,f8,f9,f23"

        all_data = []
        page = 1
        page_size = 100 
        
        # 使用Session对象复用TCP连接
        session = requests.Session()
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 配置重试策略
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        while True:
            # 动态更新分页参数
            params = {
                "pn": page,
                "pz": page_size,
                "po": "1",
                "np": "1",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fltt": "1",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0 t:6 f:!2,m:0 t:80 f:!2,m:1 t:2 f:!2,m:1 t:23 f:!2,m:0 t:81 s:262144 f:!2",
                "fields": fields,
                "dect": "1",
                "wbp2u": "|0|0|0|web",
            }
            
            try:
                # 使用较短的超时，避免长时间挂起
                # verify=False 忽略SSL证书验证（可能是代理导致证书问题）
                # 不再显式禁用代理，使用系统默认配置
                resp = session.get(
                    url, 
                    params=params, 
                    headers=headers, 
                    timeout=15, 
                    verify=False
                )
                data_json = resp.json()
                
                if not data_json.get("data") or not data_json["data"].get("diff"):
                    break
                
                diff = data_json["data"]["diff"]
                all_data.extend(diff)
                
                # 分页结束判断
                total = data_json["data"].get("total", 0)
                if len(all_data) >= total or len(diff) < page_size:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"StockProvider Error fetching page {page}: {e}")
                break
        
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        
        # 字段映射
        rename_map = {
            "f12": "代码",
            "f14": "名称",
            "f6": "成交额",
            "f2": "最新价"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # 类型转换
        df["成交额"] = pd.to_numeric(df["成交额"], errors="coerce")
        df["最新价"] = pd.to_numeric(df["最新价"], errors="coerce")
        
        return df

stock_provider = StockProvider()
