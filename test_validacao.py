import csv
import glob
import math
import os
import pytest

# Identifica automaticamente todos os arquivos CSV de resultado no diretório
ARQUIVOS_CSV = glob.glob("resultado_memoria_*.csv")

# Caso nenhum arquivo com padrão de nome seja encontrado, busca nomes padrão
if not ARQUIVOS_CSV:
    ARQUIVOS_CSV = [
        f
        for f in [
            "resultado_memoria_windows.csv",
            "resultado_memoria_linux.csv",
            "resultado_memoria.csv",
        ]
        if os.path.exists(f)
    ]


@pytest.fixture(params=ARQUIVOS_CSV if ARQUIVOS_CSV else ["SEM_ARQUIVO"])
def csv_dados(request):
    caminho = request.param
    assert os.path.exists(caminho), (
        f"Nenhum arquivo CSV para validação encontrado. Verifique se o arquivo"
        f" '{caminho}' existe no diretório."
    )
    with open(caminho, mode="r", encoding="utf-8") as f:
        leitor = list(csv.reader(f))
    assert len(leitor) > 0, f"O arquivo '{caminho}' está vazio."
    cabecalho = [col.strip() for col in leitor[0]]
    linhas = leitor[1:]
    return {"caminho": caminho, "cabecalho": cabecalho, "linhas": linhas}


# -----------------------------------------------------------------------------
# 1. VALIDAÇÃO: Cabeçalho correto
# -----------------------------------------------------------------------------
def test_cabecalho_correto(csv_dados):
    """Valida se o arquivo possui exatamente as 6 colunas previstas na ordem oficial."""
    cabecalho_esperado = [
        "bloco_MB",
        "teste",
        "alloc_ms",
        "write_ms",
        "read_ms",
        "free_ms",
    ]
    assert csv_dados["cabecalho"] == cabecalho_esperado, (
        f"Cabeçalho incorreto em '{csv_dados['caminho']}'.\n"
        f"Esperado: {cabecalho_esperado}\n"
        f"Encontrado: {csv_dados['cabecalho']}"
    )


# -----------------------------------------------------------------------------
# 2. VALIDAÇÃO: 1.000 registros
# -----------------------------------------------------------------------------
def test_quantidade_registros(csv_dados):
    """Valida se o arquivo contém exatamente 1.000 linhas de dados (excluindo o cabeçalho)."""
    total_registros = len(csv_dados["linhas"])
    assert total_registros == 1000, (
        f"Quantidade de registros incorreta em '{csv_dados['caminho']}'. "
        f"Esperado: 1000 registros, Encontrado: {total_registros}."
    )


# -----------------------------------------------------------------------------
# 3. VALIDAÇÃO: 10 tamanhos e 100 testes (sem ausências ou duplicatas)
# -----------------------------------------------------------------------------
def test_10_tamanhos_e_100_testes(csv_dados):
    """Valida a cobertura completa dos 10 tamanhos de bloco (100 a 1000 MB) e 100 testes por bloco."""
    tamanhos_esperados = set(range(100, 1100, 100))
    combinacoes_encontradas = set()
    tamanhos_encontrados = set()
    contagem_por_tamanho = {mb: 0 for mb in tamanhos_esperados}

    for idx, linha in enumerate(csv_dados["linhas"], start=2):
        assert len(linha) >= 2, (
            f"Linha {idx} em '{csv_dados['caminho']}' não possui colunas suficientes."
        )
        try:
            bloco_mb = int(linha[0].strip())
            teste_num = int(linha[1].strip())
        except ValueError:
            pytest.fail(
                f"Linha {idx} em '{csv_dados['caminho']}': 'bloco_MB' ({linha[0]}) ou"
                f" 'teste' ({linha[1]}) não são inteiros válidos."
            )

        tamanhos_encontrados.add(bloco_mb)

        # Verificação de unicidade (sistema/bloco/teste)
        chave = (bloco_mb, teste_num)
        assert chave not in combinacoes_encontradas, (
            f"Duplicidade encontrada na linha {idx} de '{csv_dados['caminho']}':"
            f" bloco_MB={bloco_mb}, teste={teste_num}."
        )
        combinacoes_encontradas.add(chave)

        if bloco_mb in contagem_por_tamanho:
            contagem_por_tamanho[bloco_mb] += 1

    # Confere se os 10 tamanhos de bloco estão presentes
    assert tamanhos_encontrados == tamanhos_esperados, (
        f"Tamanhos de bloco incorretos em '{csv_dados['caminho']}'. "
        f"Esperados: {sorted(tamanhos_esperados)}, Encontrados:"
        f" {sorted(tamanhos_encontrados)}."
    )

    # Confere se há exatamente 100 repetições por tamanho
    for mb, qtd in contagem_por_tamanho.items():
        assert qtd == 100, (
            f"O bloco de {mb} MB possui {qtd} repetições em '{csv_dados['caminho']}'"
            " (esperado: 100)."
        )


# -----------------------------------------------------------------------------
# 4. VALIDAÇÃO: Tempos válidos (numéricos, finitos e não negativos)
# -----------------------------------------------------------------------------
def test_tempos_validos(csv_dados):
    """Valida se todas as medições de tempo são numéricas, finitas, sem nulos e >= 0."""
    colunas_tempo = ["alloc_ms", "write_ms", "read_ms", "free_ms"]
    for idx, linha in enumerate(csv_dados["linhas"], start=2):
        for i, nome_coluna in enumerate(colunas_tempo, start=2):
            valor_str = linha[i].strip()
            assert valor_str != "", (
                f"Célula vazia na coluna '{nome_coluna}', linha {idx} em"
                f" '{csv_dados['caminho']}'."
            )
            try:
                valor_float = float(valor_str)
            except ValueError:
                pytest.fail(
                    f"Valor não numérico '{valor_str}' na coluna '{nome_coluna}', linha"
                    f" {idx} em '{csv_dados['caminho']}'."
                )
            assert math.isfinite(valor_float), (
                f"Valor não finito ({valor_float}) na coluna '{nome_coluna}', linha"
                f" {idx} em '{csv_dados['caminho']}'."
            )
            assert valor_float >= 0.0, (
                f"Tempo negativo ({valor_float} ms) na coluna '{nome_coluna}', linha"
                f" {idx} em '{csv_dados['caminho']}'."
            )


# -----------------------------------------------------------------------------
# 5. VALIDAÇÃO: Mesmo esquema e unidade (6 colunas, tipos corretos)
# -----------------------------------------------------------------------------
def test_mesmo_esquema_e_unidade(csv_dados):
    """Valida a consistência de tipos e número exato de 6 colunas por registro."""
    for idx, linha in enumerate(csv_dados["linhas"], start=2):
        assert len(linha) == 6, (
            f"Linha {idx} em '{csv_dados['caminho']}' possui {len(linha)} colunas"
            " (esperado: 6)."
        )
        # bloco_MB e teste devem ser inteiros
        assert linha[0].strip().isdigit(), (
            f"Linha {idx}: 'bloco_MB' ({linha[0]}) deve ser um número inteiro."
        )
        assert linha[1].strip().isdigit(), (
            f"Linha {idx}: 'teste' ({linha[1]}) deve ser um número inteiro."
        )
        # As 4 métricas devem ser conversíveis para float (milissegundos)
        for col_idx in range(2, 6):
            try:
                float(linha[col_idx].strip())
            except ValueError:
                pytest.fail(
                    f"Linha {idx}, coluna {col_idx} em '{csv_dados['caminho']}' não é"
                    " um tempo válido em ms."
                )