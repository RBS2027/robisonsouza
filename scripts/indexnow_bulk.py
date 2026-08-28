# -*- coding: utf-8 -*-
"""Envia todas as URLs do sitemap.xml ao IndexNow (Bing/Yandex) em uma unica chamada."""
import re, json, urllib.request

DOMAIN = "robisonsouza.com.br"
KEY = "9464809730abec9a7e1cbb95623945ff"

with open("sitemap.xml", encoding="utf-8") as f:
    content = f.read()
urls = re.findall(r"<loc>([^<]+)</loc>", content)
print(f"URLs encontradas: {len(urls)}")

payload = {
    "host": DOMAIN,
    "key": KEY,
    "keyLocation": f"https://{DOMAIN}/{KEY}.txt",
    "urlList": urls,
}
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("Status:", resp.status)
except Exception as e:
    print("Falha no envio (nao critico):", e)
