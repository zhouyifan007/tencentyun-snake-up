import requests
import json
import time  
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# 重要：请先运行get_cookies.py获取登录后的cookies，并确保cookies.json文件存在且格式正确
session = requests.Session()

# 加载Cookie（确保cookies.json文件格式正确）
with open("cookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)
    for cookie in cookies:
        # 兼容Cookie字段缺失的情况
        session.cookies.set(
            cookie.get('name', ''),
            cookie.get('value', ''),
            domain=cookie.get('domain', ''),
            path=cookie.get('path', '/')  # 默认路径为/
        )


check_data = {
    "activity_id": 162634773874417,
    "goods": [
        {
            "act_id": 1784747698901873,
            "region_id": [1,4,8]
        }
    ],
    "preview": 0
}


headers = {
    "x-csrf-token": str(1098793468),  # 需从浏览器实时获取
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "referer": "https://cloud.tencent.com/act/pro/featured-202607?fromSource=gwzcw.10216579.10216579.10216579&utm_medium=cpc&utm_id=gwzcw.10216579.10216579.10216579&msclkid=9d471e943d2d142808a4771f328779e6&page=warmup-202606&s_source=https%3A%2F%2Fcloud.tencent.com%2Fact%2Fpro%2Fdouble12-2025"
}

# =================== 检查是否可抢购 =================== #

def check_available():
    """
    检查库存，返回有货的地域ID（无货返回None）
    """
    try:
        resp = session.post(
            "https://act-api.cloud.tencent.com/dianshi/check-available",
            json=check_data,
            headers=headers,
            timeout=10  # 新增超时控制
        )
        resp.raise_for_status()  # 抛出HTTP错误（4xx/5xx）
        result = resp.json()
    except Exception as e:
        print(f"❌ 库存检查接口调用失败：{str(e)}")
        return None

    # 校验接口返回是否正常
    if result.get("code") != 0 or result.get("msg") != "ok":
        print(f"❌ 库存检查接口返回异常：{json.dumps(result, ensure_ascii=False)}")
        return None

    # 校验商品基础权限（修复：逻辑反转）
    goods_data = result.get("data", [{}])[0]
    if goods_data.get("available") != 1 or goods_data.get("user_available") != 1:
        print("❌ 商品无购买权限/整体无货")
        return None

    # 安全获取地域库存（修复：避免KeyError）
    quota = goods_data.get("quota", {})
    # 优先级：1（华北）→4（华东）→8（华南）
    region_map = {
        1: "华北",
        4: "华东",
        8: "华南",
    }
    for region_id, region_name in region_map.items():
        # 逐层get，避免字段缺失报错
        available = quota.get(str(region_id), {})\
                        .get("bundle_budget_mc_lg4_01", {})\
                        .get("available", 0)
        if available > 0:
            print(f"✅ 检测到{region_name}（region_id={region_id}）有库存！")
            return region_id

    # 所有地域无货
    print("❌ 所有目标地域均无库存")
    return None


    """调用prepare-do接口（抢购准备）"""
    try:
        resp = session.post(
            "https://act-api.cloud.tencent.com/dianshi/prepare-do",
            json=pay_data,
            headers=headers,
            timeout=10
        )
        print(f"📌 抢购准备接口返回：{resp.text}")
        return resp.json()
    except Exception as e:
        print(f"❌ 抢购准备接口调用失败：{str(e)}")
        return None

# =================== 立即购买（核心下单） =================== #
def buy_now(region_id):
    """
    调用do-goods接口完成购买
    :param region_id: 有货的地域ID
    """
    do_data = {
        "activity_id": 162634773874417,
        "agent_channel": {
            "fromChannel": "",
            "fromSales": "",
            "isAgentClient": False,
            "fromUrl": "https://cloud.tencent.com/act/pro/featured-202607?fromSource=gwzcw.10216579.10216579.10216579&utm_medium=cpc&utm_id=gwzcw.10216579.10216579.10216579&msclkid=9d471e943d2d142808a4771f328779e6&page=warmup-202606&s_source=https%3A%2F%2Fcloud.tencent.com%2Fact%2Fpro%2Fdouble12-2025"
        },
        
        "business": {
            "id": 22755,
            "from": "lightningDeals"
        },
        "goods": [
            {
                "act_id": 1897632168296710,
                "type": "bundle_budget_mc_lg4_01",
                "goods_param": {
                    "BlueprintId": "LINUX_UNIX",
                    "area": 1,
                    "ddocUnionConnect": 0,
                    "goodsNum": 1,
                    "imageId": "lhbp-eqora508",
                    "scenario": "0",
                    "timeSpanUnit": "12m",
                    "zone": "",
                    "regionId": region_id,
                    "type": "bundle_budget_mc_lg4_01"
                }
            }
        ],
        
        "preview": 0
    }
    try:
        # 修复：传do_data而非pay_data
        resp = session.post(
            "https://act-api.cloud.tencent.com/dianshi/do-goods",
            json=do_data,  # 关键修复：使用正确的购买参数
            headers=headers,
            timeout=10
        )
        print(f"🎯 核心购买接口返回：{resp.text}")
        return resp.json()
    except Exception as e:
        print(f"❌ 核心购买接口调用失败：{str(e)}")
        return None
    
def get_server_time():
    """获取服务器时间，校准本地时间"""
    url = "https://cloud.tencent.com/act/pro/double12-2025"
    response = requests.head(url)
    server_time = response.headers.get("Date")

    if server_time:
        dt = datetime.strptime(server_time, "%a, %d %b %Y %H:%M:%S GMT")
        beijing_time = dt + timedelta(hours=8)
        timestamp_ms = int(beijing_time.timestamp() * 1000)
        print(f"服务器时间(GMT): {dt}")
        print(f"北京时间: {beijing_time}")
        print(f"时间戳(毫秒): {timestamp_ms}")
        return timestamp_ms
    else:
        print("未获取到服务器时间")
        return None

def buy_now_concurrent(region_ids):
    """并发抢购多个地域"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(buy_now, rid) for rid in region_ids]
        for future in futures:
            result = future.result()
            if isinstance(result, dict) and result.get("code") == 0:
                print(f"🎉 抢购成功！地域ID: {result.get('region_id', '未知')}")
                return result
            # 也可以打印失败信息，方便调试
            else:
                print(f"地域 {result.get('region_id', '未知')} 抢购失败: {result}")
    return None

# =================== 主程序 =================== #
if __name__ == "__main__":
    print("🚀 启动腾讯云抢购脚本...")
    SECKILL_TIME_STR = "2026-02-12 15:00:00" # 秒杀开始时间（北京时间）可以更改为10:00:00,此处需要更改为实际的秒杀时间
    SECKILL_TIMESTAMP = int(time.mktime(time.strptime(SECKILL_TIME_STR, "%Y-%m-%d %H:%M:%S"))) * 1000
    region_ids = [1, 4, 8]
    
    
    while True:
        current_time = get_server_time()
        if current_time >= SECKILL_TIMESTAMP:
            print("秒杀开始！")
            buy_now_concurrent(region_ids)
            break
        else:
            print(f"⏳ 当前时间未到达秒杀时间，当前服务器时间: {current_time}, 秒杀时间: {SECKILL_TIMESTAMP}")
