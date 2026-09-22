import csv
import gc
import platform
import time

# -----------------------------------------------------------------------------
# PARÂMETROS DO EXPERIMENTO
# -----------------------------------------------------------------------------
# 10 tamanhos de bloco: 100 MB até 1.000 MB (passo de 100 MB)
TAMANHOS_MB = list(range(100, 1100, 100))

# 100 repetições para cada tamanho de bloco (totalizando 1.000 registros por SO)
REPETICOES = 100

# Nome do arquivo CSV de saída (identifica automaticamente o SO em execução)
so_nome = platform.system().lower()
NOME_ARQUIVO_CSV = f"resultado_memoria_{so_nome}.csv"


def executar_benchmark():
    print("=" * 65)
    print(
        f"Iniciando Benchmark de Memória no SO: {platform.system()}"
        f" ({platform.release()})"
    )
    print(f"Arquitetura: {platform.machine()} | Python: {platform.python_version()}")
    print(f"Arquivo de saída: {NOME_ARQUIVO_CSV}")
    print("=" * 65)

    # Abertura do arquivo CSV no padrão recomendado (encoding utf-8 e newline='')
    with open(NOME_ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq)

        # 1. Cabeçalho obrigatório (6 colunas)
        escritor.writerow(
            ["bloco_MB", "teste", "alloc_ms", "write_ms", "read_ms", "free_ms"]
        )

        total_registros = 0

        for mb in TAMANHOS_MB:
            bloco_bytes = mb * 1024 * 1024  # Conversão de MB para Bytes
            print(f"\n[+] Executando bloco de {mb} MB...")

            for t in range(1, REPETICOES + 1):
                # Coleta de lixo prévia para impedir intervenção do GC durante as medições
                gc.collect()

                # -----------------------------------------------------------------
                # 1. ALOCAÇÃO DE MEMÓRIA (bytearray)
                # -----------------------------------------------------------------
                t0 = time.perf_counter_ns()
                bloco = bytearray(bloco_bytes)
                t1 = time.perf_counter_ns()
                alloc_ms = (t1 - t0) / 1_000_000

                # Preparação do padrão de bytes (executada FORA do intervalo de medição)
                padrao = b"\xAA" * len(bloco)

                # -----------------------------------------------------------------
                # 2. ESCRITA DE MEMÓRIA (Atribuição ao conteúdo do bloco)
                # -----------------------------------------------------------------
                t2 = time.perf_counter_ns()
                bloco[:] = padrao
                t3 = time.perf_counter_ns()
                write_ms = (t3 - t2) / 1_000_000

                # -----------------------------------------------------------------
                # 3. LEITURA DE MEMÓRIA (Varredura e soma dos bytes)
                # -----------------------------------------------------------------
                t4 = time.perf_counter_ns()
                _soma = sum(bloco)
                t5 = time.perf_counter_ns()
                read_ms = (t5 - t4) / 1_000_000

                # -----------------------------------------------------------------
                # 4. LIBERAÇÃO LÓGICA DE MEMÓRIA (Esvaziamento e deleção)
                # -----------------------------------------------------------------
                t6 = time.perf_counter_ns()
                bloco.clear()
                del bloco
                t7 = time.perf_counter_ns()
                free_ms = (t7 - t6) / 1_000_000

                # -----------------------------------------------------------------
                # REGISTRO NO ARQUIVO CSV
                # -----------------------------------------------------------------
                escritor.writerow([
                    mb,
                    t,
                    f"{alloc_ms:.6f}",
                    f"{write_ms:.6f}",
                    f"{read_ms:.6f}",
                    f"{free_ms:.6f}",
                ])

                total_registros += 1

            print(f" -> {REPETICOES} repetições concluídas para {mb} MB.")

    print("\n" + "=" * 65)
    print(
        f"Benchmark finalizado com sucesso! {total_registros} registros salvos em"
        f" '{NOME_ARQUIVO_CSV}'."
    )
    print("=" * 65)


if __name__ == "__main__":
    executar_benchmark()