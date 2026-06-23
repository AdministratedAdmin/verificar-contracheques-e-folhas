import pdfplumber
import re

def analisar_contracheque(arquivo):
    resultados = []
    erros = 0 

    with pdfplumber.open(arquivo) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if not texto:
                continue

            padraonome = r"""
            \b\d+[.:–\-]?\s+
            (?!Matr[ií]cula|Data|\nCargo|Fun[cç][aã]o|CPF)
            ([A-ZÀ-Ú]+(?:\s(?:DA|DE|DO|DOS|DAS|E)?\s?[A-ZÀ-Ú]{2,}){1,3})
            """

            padraopericulosidade = r"PERICULOSIDADE.*?R\$[\s]?(\d{1,3}(?:\.\d{3})*,\d{2})"
            padraosalario = r"SALARIO MES CIVIL.*?R\$[\s]?(\d{1,3}(?:\.\d{3})*,\d{2})"

            nomes = re.findall(padraonome, texto, re.VERBOSE)
            nomevigilante = nomes[1] if len(nomes) >= 2 else "Não encontrado"

            periculosidadebruta = re.findall(padraopericulosidade, texto)
            periculosidade = [float(v.replace('.', '').replace(',', '.')) for v in periculosidadebruta]

            salariobruto = re.findall(padraosalario, texto)
            salario = [float(s.replace('.', '').replace(',', '.')) for s in salariobruto]

            if salario and periculosidade:
                if round(periculosidade[0], 2) == round(salario[0] * 0.3, 2):
                    pericuconformidade = "Está em conformidade"
                else:
                    pericuconformidade = "Não está em conformidade"
                    erros += 1
            else:
                pericuconformidade = "Dados insuficientes"
                erros += 1

            resultados.append(
                f"Página {i}\n"
                f"Vigilante: {nomevigilante}\n"
                f"Salário Bruto: {salario}\n"
                f"Periculosidade: {periculosidade}\n"
                f"Resultado: {pericuconformidade}\n"
            )

    if not resultados:
        return "Nenhum dado válido encontrado no arquivo."

    if erros == 0:
        resultados.append("\nTudo está em conformidade\n")
    else:
        resultados.append(f"\nTotal de erros encontrados: {erros}\n")

    return "\n".join(resultados)
