# MicrobenchmarkOperacoesEmMemoria
 T2 - Microbenchmark de Operacoes em Memoria

---

### Rodar Testes 
``` python -m pytest test_validacao.py -q ```

---

### Parâmetros e Tamanhos de Bloco
* **Tamanhos de Bloco de Memória:** 10 tamanhos sequenciais, variando de **100 MB a 1.000 MB**, com incrementos de **100 MB** (`100, 200, 300, 400, 500, 600, 700, 800, 900 e 1.000 MB`).
* **Repetições (Testes):** 100 execuções para cada tamanho de bloco.
* **Volume de Dados:** Total de **1.000 registros por sistema operacional** (2.000 registros no experimento completo).
* **Estrutura de Operações:**
  1. **Alocação:** Criação de bloco mutável de bytes via `bytearray`.
  2. **Escrita:** Atribuição do padrão de bytes ao bloco.
  3. **Leitura:** Varredura e somatório sequencial dos bytes (`sum()`).
  4. **Liberação:** Esvaziamento e deleção lógica do bloco (`clear()` e `del`).

---
### Ambiente
* **Versão Única do Python:** Foi utilizada a **mesma versão do Python (3.14.4)** em ambos os ambientes (Windows e Linux).
* **Isolamento de Execução (Shutdown das VMs):** Apenas **uma máquina virtual permaneceu em execução por vez**. Enquanto um sistema operacional passava pelos testes de benchmark, a outra VM mantinha-se **desligada (shutdown completo)**.

* **Recursos Alocados:** Ambas as VMs foram configuradas com 4 vCPUs e 4 GB de memória RAM no mesmo hardware hospedeiro.

---
### Testes
O `pytest` executa as 5 asserções principais de controle de qualidade (Checkpoints 1 e 2):

1. **Cabeçalho Obrigatório:** Verifica se a primeira linha contém exatamente o esquema de 6 colunas previsto (`bloco_MB,teste,alloc_ms,write_ms,read_ms,free_ms`).
2. **Volume Exato de Registros:** Confirma a presença de exatamente **1.000 linhas de dados** por arquivo CSV (excluindo o cabeçalho).
3. **Cobertura de Blocos e Testes:** Valida se existem 100 repetições sequenciais (1 a 100) para cada um dos 10 tamanhos de bloco (100 a 1000 MB), garantindo ausência de duplicidades ou omissões de teste.
4. **Validade das Medições de Tempo:** Garante que todos os tempos medidos em milissegundos (`alloc_ms`, `write_ms`, `read_ms`, `free_ms`) são valores numéricos finitos e não negativos (`>= 0.0`).
5. **Consistência de Esquema e Unidade:** Confirma o tipo de dados correto para cada coluna (inteiros para `bloco_MB` e `teste`, ponto flutuante para as métricas temporais em ms).

---