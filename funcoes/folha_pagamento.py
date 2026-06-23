import pdfplumber
import re


def analisar_folha_pagamento(arquivo):

    resultados = []
    erros = 0

    # Padrões regex
    padraonome = r'Empr\.\:\s*(\d*[A-ZÀ-Ú][A-ZÀ-Ú\s\-]*)\s*Situação'
    padrao_periculosidade = re.compile(
        r'(?i)(?:PERICULOSIDADE)\s*\d{1,3},\d{2}\s+([0-9]{1,3}(?:\.[0-9]{3})*,\d{2})(?=P)'
    )

    def str_para_float(valor_str):
        if not valor_str:
            return None
        s = valor_str.replace('.', '').replace(',', '.').strip()
        try:
            return float(s)
        except ValueError:
            return None

    def extrair_periculosidade_por_pagina(texto, max_por_pagina=5):
        encontrados = padrao_periculosidade.findall(texto)
        resultados = []
        for v in encontrados[:max_por_pagina]:
            f = str_para_float(v)
            if f and f > 0:
                resultados.append(f)
        return resultados

    with pdfplumber.open(arquivo) as pdf:
        for pagina_idx, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""

            nomes = re.findall(padraonome, texto)
            nomes = [
                re.sub(r'^\d+', '', nome).strip()
                for nome in nomes if nome.strip()
            ][:5]

            if not nomes:
                continue

            salarios = re.findall(r'(?i)sal[áa]rio:\s*([\d\.\,]+)', texto)[:5]
            salarios = [str_para_float(v) for v in salarios if str_para_float(v) is not None]

            periculosidades = extrair_periculosidade_por_pagina(texto, max_por_pagina=5)

            for idx, nome in enumerate(nomes):
                s = salarios[idx] if idx < len(salarios) else 0
                p = periculosidades[idx] if idx < len(periculosidades) else 0

                if s > 0 and p > 0:
                    if round(p, 2) == round(s * 0.3, 2):
                        conformidade = "Está em conformidade"
                    else:
                        conformidade = "Não está em conformidade"
                else:
                    conformidade = "Dados insuficientes"

                resultados.append(
                    f"Página {pagina_idx}\n"
                    f"Funcionário: {nome}\n"
                    f"Salário: R$ {s:.2f}\n"
                    f"Periculosidade: R$ {p:.2f}\n"
                    f"Resultado: {conformidade}\n"
                )

    if not resultados:
        return "Nenhum dado válido encontrado no arquivo."

    if erros == 0:
        resultados.append("\nTudo está em conformidade\n")
    else:
        resultados.append(f"\nTotal de erros encontrados: {erros}\n")

    return "\n".join(resultados)
