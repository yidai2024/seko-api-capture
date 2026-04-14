#!/usr/bin/env python3
"""seko.sensetime.com API 抓取脚本"""

from playwright.sync_api import sync_playwright
import json, time
from datetime import datetime
from urllib.parse import urlparse

def capture():
    all_apis = []
    seen = set()
    skip_ext = ['.js','.css','.png','.jpg','.jpeg','.gif','.svg','.woff','.woff2','.ttf','.ico','.webp','.mp4','.m3u8','.map','.xml','.txt','.eot','.wasm']

    def on_req(req):
        url = req.url
        if any(url.lower().endswith(e) for e in skip_ext): return
        if url.startswith(('data:','blob:')): return
        if url not in seen:
            seen.add(url)
            parsed = urlparse(url)
            info = {
                'url': url, 'method': req.method,
                'domain': parsed.netloc, 'path': parsed.path,
                'query': parsed.query,
                'timestamp': datetime.now().isoformat(),
                'headers': dict(req.headers),
                'post_data': None
            }
            if req.method in ('POST','PUT','PATCH','DELETE'):
                try: info['post_data'] = req.post_data[:8000]
                except: pass
            all_apis.append(info)

    def on_resp(resp):
        for api in all_apis:
            if api['url'] == resp.url:
                api['status'] = resp.status
                api['content_type'] = resp.headers.get('content-type','')
                api['resp_headers'] = dict(resp.headers)
                try:
                    ct = api.get('content_type','')
                    if 'json' in ct or 'text' in ct:
                        api['resp_body'] = resp.text()[:5000]
                except: pass
                break

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(
            viewport={'width':1920,'height':1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN'
        )
        page = ctx.new_page()
        page.on('request', on_req)
        page.on('response', on_resp)

        # 多页面访问
        pages_to_visit = [
            ('https://seko.sensetime.com/explore', '探索页'),
            ('https://seko.sensetime.com/', '首页'),
            ('https://seko.sensetime.com/create', '创作'),
            ('https://seko.sensetime.com/workspace', '工作台'),
            ('https://seko.sensetime.com/login', '登录'),
            ('https://seko.sensetime.com/signup', '注册'),
            ('https://seko.sensetime.com/pricing', '价格'),
            ('https://seko.sensetime.com/gallery', '画廊'),
            ('https://seko.sensetime.com/models', '模型'),
            ('https://seko.sensetime.com/community', '社区'),
            ('https://seko.sensetime.com/docs', '文档'),
            ('https://seko.sensetime.com/api', 'API'),
            ('https://seko.sensetime.com/settings', '设置'),
            ('https://seko.sensetime.com/profile', '个人'),
            ('https://seko.sensetime.com/billing', '账单'),
        ]
        
        for url, name in pages_to_visit:
            print(f"\n--- {name} ({url}) ---")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(4)
                # 滚动加载
                for _ in range(5):
                    page.evaluate('window.scrollBy(0, 800)')
                    time.sleep(1)
                page.screenshot(path=f'/root/seko_{name}.png')
                print(f"  ✓ 请求数: {len(all_apis)} | Status: {page.url}")
                
                # 提取链接
                links = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                        .filter(h => h.includes('sensetime.com'))
                        .filter((v,i,a) => a.indexOf(v) === i).slice(0, 15);
                }''')
                if links:
                    for l in links[:8]:
                        print(f"    → {l[:70]}")
            except Exception as e:
                print(f"  ✗ {str(e)[:60]}")
        
        # 点击按钮
        print("\n=== 点击交互 ===")
        try:
            page.goto('https://seko.sensetime.com/explore', wait_until='domcontentloaded', timeout=20000)
            time.sleep(3)
            btns = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('button, [role="button"], a[class*="btn"]'))
                    .map(b => ({text: b.textContent.trim().substring(0,50), tag: b.tagName}))
                    .filter(b => b.text.length > 0 && b.text.length < 40);
            }''')
            print(f"  按钮数: {len(btns)}")
            for b in btns[:15]:
                print(f"    [{b['tag']}] {b['text']}")
            
            for b in btns[:10]:
                try:
                    page.click(f'text="{b["text"][:25]}"', timeout=3000)
                    time.sleep(2)
                    print(f"    ✓ 点击: {b['text'][:25]}")
                except: pass
        except Exception as e:
            print(f"  点击失败: {e}")
        
        # 从JS提取API
        print("\n=== JS中的API端点 ===")
        js_apis = page.evaluate('''() => {
            const found = [];
            document.querySelectorAll('script:not([src])').forEach(s => {
                const t = s.textContent;
                (t.match(/["'](\/api\/[^"']{2,120})["']/g) || []).forEach(m => found.push(m));
                (t.match(/["'](\/v[0-9]+\/[^"']{2,120})["']/g) || []).forEach(m => found.push(m));
                (t.match(/fetch\s*\(\s*["']([^"']+)["']/g) || []).forEach(m => found.push('fetch: '+m));
                (t.match(/["'](https?:\/\/[^"']*(?:api|service|gateway|backend|sensetime)[^"']*)["']/gi) || []).forEach(m => found.push('url: '+m));
            });
            if (window.__INITIAL_STATE__) found.push('global: __INITIAL_STATE__');
            if (window.__NEXT_DATA__) found.push('global: __NEXT_DATA__');
            if (window.__NUXT__) found.push('global: __NUXT__');
            return [...new Set(found)];
        }''')
        for j in js_apis:
            print(f"  {j}")
        
        # 保存HTML
        html = page.content()
        with open('/root/seko_explore.html', 'w') as f:
            f.write(html)
        print(f"\n  HTML已保存: {len(html)} bytes")
        
        browser.close()
    return all_apis

if __name__ == '__main__':
    print(f"开始抓取 seko.sensetime.com ... {datetime.now()}")
    apis = capture()
    
    with open('/root/seko_raw_apis.json', 'w', encoding='utf-8') as f:
        json.dump(apis, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n抓取完成! 共 {len(apis)} 个请求")
    by_domain = {}
    for a in apis:
        d = a['domain']
        by_domain[d] = by_domain.get(d, 0) + 1
    for d, c in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
