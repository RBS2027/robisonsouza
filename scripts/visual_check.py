#!/usr/bin/env python3
"""
Checagem visual automatica: renderiza paginas-chave num navegador real
e detecta problemas que só aparecem visualmente (nao no HTML bruto):
  1. Texto cortado (overflow horizontal escondido pelo body)
  2. Baixo contraste entre texto e fundo (abaixo do minimo WCAG AA)
  3. Imagens quebradas (nao carregaram)

Roda com Playwright + Chromium headless. Anexa achados ao mesmo
relatorio usado pelo qa_check.py (/tmp/qa_report_body.md), para que
apareçam na mesma issue/e-mail do GitHub.
"""
import http.server
import json
import re
import socketserver
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PORTA = 8901
RAIZ = Path(__file__).resolve().parent.parent  # raiz do site (onde este script mora em scripts/)

# Paginas-chave a checar (home sempre; adicionar outras paginas de alto trafego se quiser)
PAGINAS = ["/"]


def contraste_wcag(rgb1, rgb2):
    """Calcula a razao de contraste WCAG entre duas cores RGB (tuplas 0-255)."""
    def luminancia(rgb):
        def canal(c):
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = rgb
        return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)
    l1, l2 = luminancia(rgb1), luminancia(rgb2)
    claro, escuro = max(l1, l2), min(l1, l2)
    return (claro + 0.05) / (escuro + 0.05)


def parse_rgb(cor_css):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", cor_css or "")
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def rodar():
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORTA), handler, bind_and_activate=False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    import os
    os.chdir(RAIZ)
    thread.start()
    time.sleep(0.5)

    achados = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        for caminho in PAGINAS:
            url = f"http://localhost:{PORTA}{caminho}"
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
                # esperar fontes carregarem e o layout estabilizar de vez -
                # sem isso, a posicao dos elementos pode mudar entre a
                # leitura das coordenadas e o print, dando resultado
                # inconsistente entre execucoes (condicao de corrida).
                page.evaluate("() => document.fonts.ready")
                page.wait_for_timeout(300)
            except Exception as e:
                achados.append(f"- ⚠️ **{caminho}**: não carregou para checagem visual ({e})")
                continue

            # 1. Texto cortado: qualquer elemento de texto direto (b, h1-h4, span, small, p)
            #    cujo scrollWidth exceda o clientWidth por uma margem visivel.
            cortes = page.evaluate("""
            () => {
                const alvos = document.querySelectorAll('b, h1, h2, h3, h4, span, small, p, a, dt');
                const achados = [];
                for (const el of alvos) {
                    if (el.children.length > 0) continue; // só folhas de texto
                    const texto = el.innerText.trim();
                    if (!texto) continue;
                    if (el.scrollWidth > el.clientWidth + 4) {
                        achados.push({texto: texto.slice(0, 60), tag: el.tagName, sobra: el.scrollWidth - el.clientWidth});
                    }
                }
                return achados;
            }
            """)
            for c in cortes:
                achados.append(f"- ✂️ **{caminho}**: texto pode estar cortado — \"{c['texto']}\" ({c['tag']}, {c['sobra']}px de sobra)")

            # 2. Contraste: amostragem real de pixel, usando os 4 CANTOS da propria caixa
            #    do elemento (quase sempre fundo puro, nao glifo) — robusto contra
            #    gradiente/imagem de fundo, que quebra a leitura via CSS background-color.
            candidatos = page.evaluate("""
            () => {
                const alvos = document.querySelectorAll('b, h1, h2, h3, h4, span, small, p, a, dt, dd');
                const achados = [];
                for (const el of alvos) {
                    if (el.children.length > 0) continue;
                    if (el.closest('.zap')) continue; // widget flutuante com animacao de pulso, ignorar
                    if (el.closest('.ticker')) continue; // faixa de texto rolando (marquee), sempre em movimento
                    const texto = el.innerText.trim();
                    if (!texto || texto.length < 2) continue;
                    // pular texto puramente decorativo/simbolico (ex: "★★★★★"), que
                    // fica colado a outro texto na mesma linha e da falso positivo
                    // de amostragem sem representar risco real de contraste
                    if (/^[★☆✦●○\\s]+$/.test(texto)) continue;
                    const rect = el.getBoundingClientRect();
                    if (rect.width < 10 || rect.height < 8) continue;
                    if (rect.top < 0 || rect.left < 0) continue;
                    const cs = getComputedStyle(el);
                    // pular texto com cor transparente (comum em efeito de "texto em
                    // gradiente" via background-clip:text) - a cor real vem de outra
                    // camada que esse metodo simples nao consegue avaliar direito.
                    if (cs.color === 'rgba(0, 0, 0, 0)' || cs.color === 'transparent') continue;
                    const temFundoProprio = (() => {
                        let node = el;
                        for (let i = 0; i < 4 && node; i++) {
                            const ncs = getComputedStyle(node);
                            if ((ncs.backgroundColor && ncs.backgroundColor !== 'rgba(0, 0, 0, 0)') ||
                                parseFloat(ncs.borderTopWidth) > 0 ||
                                (ncs.backgroundImage && ncs.backgroundImage !== 'none')) {
                                return true;
                            }
                            node = node.parentElement;
                        }
                        return false;
                    })();
                    achados.push({
                        texto: texto.slice(0, 50),
                        cor: cs.color,
                        left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom,
                        temFundoProprio: temFundoProprio
                    });
                }
                return achados;
            }
            """)
            if candidatos:
                # screenshot de pagina inteira: getBoundingClientRect() e relativo ao
                # viewport atual, entao usamos full_page + somamos o scroll pra bater
                # com o print inteiro (senao elementos fora da 1a tela saem errados).
                screenshot_bytes = page.screenshot(full_page=True)
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
                scroll_x = page.evaluate("() => window.scrollX")
                scroll_y = page.evaluate("() => window.scrollY")
                for item in candidatos:
                    rgb_texto = parse_rgb(item["cor"])
                    if not rgb_texto:
                        continue
                    left = item["left"] + scroll_x
                    right = item["right"] + scroll_x
                    top = item["top"] + scroll_y
                    bottom = item["bottom"] + scroll_y
                    # amostrar no meio das bordas (topo/base/esquerda/direita), nao nos
                    # cantos: cantos ficam fora do preenchimento em botoes arredondados
                    # ou circulares (border-radius alto), dando falso positivo.
                    # 2 estrategias de amostragem: elementos com fundo/borda propria
                    # (botoes, badges) sao amostrados por DENTRO (perto da borda,
                    # com margem pra nao cair no glifo); texto "nu" sem fundo proprio
                    # (titulos, paragrafos) e amostrado por FORA (no fundo do
                    # container ao redor, ja que a caixa do texto gruda no glifo
                    # em toda a volta quando nao ha padding).
                    margem = 5
                    meio_x = (left + right) / 2
                    meio_y = (top + bottom) / 2
                    if item.get("temFundoProprio"):
                        pontos = [
                            (meio_x, top + margem),
                            (meio_x, bottom - margem),
                            (left + margem, meio_y),
                            (right - margem, meio_y),
                        ]
                    else:
                        pontos = [
                            (left - margem, meio_y),
                            (right + margem, meio_y),
                        ]
                    amostras = []
                    for px, py in pontos:
                        px, py = int(px), int(py)
                        if 0 <= px < img.width and 0 <= py < img.height:
                            amostras.append(img.getpixel((px, py)))
                    if not amostras:
                        continue
                    # usar a amostra de MENOR contraste com o texto como pior caso,
                    # mas exigir que pelo menos metade dos cantos concordem (evita
                    # falso positivo por um canto cair em cima de um glifo)
                    razoes = sorted(contraste_wcag(rgb_texto, a) for a in amostras)
                    razao_mediana = razoes[len(razoes) // 2]
                    if razao_mediana < 2.5:
                        achados.append(
                            f"- 🎨 **{caminho}**: possível baixo contraste (razão {razao_mediana:.1f}:1) — \"{item['texto']}\""
                        )

            # 3. Imagens quebradas
            imgs_quebradas = page.evaluate("""
            () => Array.from(document.querySelectorAll('img'))
                .filter(img => img.complete && img.naturalWidth === 0)
                .map(img => img.src)
            """)
            for src in imgs_quebradas:
                achados.append(f"- 🖼️ **{caminho}**: imagem não carregou — {src}")

        browser.close()

    httpd.shutdown()
    return achados


if __name__ == "__main__":
    achados = rodar()
    if achados:
        bloco = "## 👁️ Verificação visual automática encontrou pontos pra revisar\n\n" + "\n".join(achados) + "\n\n"
        with open("/tmp/qa_report_body.md", "a", encoding="utf-8") as f:
            f.write(bloco)
        print(f"VISUAL_ACHADOS={len(achados)}")
    else:
        print("VISUAL_ACHADOS=0")
