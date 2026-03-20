import os
import requests
import hashlib
import time

# 配置
URL_LIST_FILE = 'siteurl.txt'
BASE_DIR = 'favicon'
SIZES = [32, 64, 128, 256, 512]
API_TEMPLATE = "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size={size}&url={url}"

def get_md5(data):
    return hashlib.md5(data).hexdigest()

def download_favicons():
    # 预创建目录
    for size in SIZES:
        os.makedirs(os.path.join(BASE_DIR, str(size)), exist_ok=True)

    if not os.path.exists(URL_LIST_FILE):
        print(f"跳过：未找到 {URL_LIST_FILE}")
        return

    with open(URL_LIST_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for url in urls:
        # 直接提取域名，例如 https://baike.baidu.com -> baike.baidu.com
        domain = url.split('//')[-1].split('/')[0]
        filename = f"{domain}.png"

        print(f"正在处理: {domain}")

        for size in SIZES:
            filepath = os.path.join(BASE_DIR, str(size), filename)
            target_api = API_TEMPLATE.format(size=size, url=url)
            
            try:
                # 本地测试时，如果报错超时，请在此处 requests.get(..., proxies=PROXIES)
                response = requests.get(target_api, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    new_content = response.content
                    # 过滤无效占位图
                    if len(new_content) < 100: continue

                    new_md5 = get_md5(new_content)

                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            if get_md5(f.read()) == new_md5:
                                continue
                    
                    with open(filepath, 'wb') as f:
                        f.write(new_content)
                    print(f"  [√] {size}px 已同步")
                time.sleep(0.3) # 稍微延迟，保护 API
            except Exception as e:
                print(f"  [!] {size}px 出错: {e}")

if __name__ == "__main__":
    download_favicons()