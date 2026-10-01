import urllib.request
import re
import json

try:
    req = urllib.request.Request('https://t.me/s/korea_kosmetika010', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    
    blocks = re.findall(r'<div class="tgme_widget_message_bubble">(.*?)<div class="tgme_widget_message_info', html, re.DOTALL)
    
    results = []
    
    for block in blocks:
        text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.DOTALL)
        text = ""
        if text_match:
            text = text_match.group(1)
            text = re.sub(r'<br/?>', '\n', text)
            text = re.sub(r'<.*?>', '', text).strip()
        
        img_match = re.search(r'background-image:url\(\'(https://cdn[^\']+)\'\)', block)
        img = img_match.group(1) if img_match else None
        
        if text or img:
            results.append({"text": text, "image": img})
            
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Done")
except Exception as e:
    print('Error:', e)
