import pandas as pd

vias = pd.read_csv(
    "2025/Via - Acidente de Trânsito - MG - Jan a Dez 2025.csv",
    sep=None, engine="python", encoding="utf-8-sig"
)

print("=== SHAPE BRUTO ===")
print(f"Total de linhas: {len(vias)}")
print(f"IDs unicos (numero_ocorrencia_associado): {vias['numero_ocorrencia_associado'].nunique()}")
print()

# colunas de via (sem as de chave/metadado)
cols_via = [c for c in vias.columns if c not in ["numero_ocorrencia_associado", "ano_fato", "mes_numerico_fato", "verificacao"]]
print(f"Colunas de via analisadas: {cols_via}")
print()

# quantas linhas por ID (independente de serem iguais ou diferentes)
contagem_linhas = vias.groupby("numero_ocorrencia_associado").size()
print("=== Distribuicao de linhas por ID ===")
dist = contagem_linhas.value_counts().sort_index()
for n, c in dist.items():
    print(f"  {n} linha(s): {c} IDs  ({c/len(contagem_linhas)*100:.2f}%)")

print()

# IDs com mais de 1 linha
ids_dup = contagem_linhas[contagem_linhas > 1].index
print(f"IDs com mais de 1 linha: {len(ids_dup)}")

if len(ids_dup) > 0:
    subset_dup = vias[vias["numero_ocorrencia_associado"].isin(ids_dup)]

    # entre esses, quantos tem linhas IDENTICAS vs DIFERENTES
    # linhas identicas = duplicatas reais
    n_linhas_dup_identicas = subset_dup.duplicated(subset=["numero_ocorrencia_associado"] + cols_via).sum()
    print(f"Linhas completamente identicas (mesmo ID + mesmos dados de via): {n_linhas_dup_identicas}")

    # contar IDs onde pelo menos uma linha difere das outras
    def tem_linha_diferente(grupo):
        return grupo[cols_via].drop_duplicates().shape[0] > 1

    ids_com_via_diferente = subset_dup.groupby("numero_ocorrencia_associado").filter(tem_linha_diferente)["numero_ocorrencia_associado"].unique()
    print(f"IDs com linhas de VIA DIFERENTES entre si: {len(ids_com_via_diferente)}")

    if len(ids_com_via_diferente) > 0:
        print("\nExemplos:")
        for ocorr_id in ids_com_via_diferente[:3]:
            print(f"\n--- {ocorr_id} ---")
            print(vias[vias["numero_ocorrencia_associado"] == ocorr_id][["numero_ocorrencia_associado"] + cols_via].to_string())
else:
    # mesmo sem linhas duplicadas, verificar se os dados batem com registros de acidentes
    # O caso que voce mencionou pode ser IDs distintos com dados parecidos, ou
    # o mesmo numero_ocorrencia_associado aparecendo em anos diferentes
    print("\nVerificando se o mesmo ID aparece em ANOS diferentes (cross-year)...")
    print(vias.groupby(["numero_ocorrencia_associado", "ano_fato"]).size().reset_index(name="n").query("n > 1").head(10))
    print()
    print("Contagem de IDs por ano:")
    print(vias.groupby("ano_fato")["numero_ocorrencia_associado"].nunique())

# Verificar dados de outros anos juntos
print("\n\n=== VERIFICANDO TODOS OS ANOS JUNTOS (2023+2024+2025) ===")
import glob

dfs = []
for ano in ["2023", "2024", "2025"]:
    arqs = glob.glob(f"{ano}/Via*.csv")
    if arqs:
        df_ano = pd.read_csv(arqs[0], sep=None, engine="python", encoding="utf-8-sig")
        df_ano["_ano_arquivo"] = ano
        dfs.append(df_ano)

vias_all = pd.concat(dfs, ignore_index=True)
print(f"Total combinado: {len(vias_all)} linhas")
print(f"IDs unicos no total: {vias_all['numero_ocorrencia_associado'].nunique()}")

contagem_all = vias_all.groupby("numero_ocorrencia_associado").size()
ids_dup_all = contagem_all[contagem_all > 1]
print(f"IDs que aparecem em mais de 1 linha (cross-year): {len(ids_dup_all)}")
if len(ids_dup_all) > 0:
    dist2 = ids_dup_all.value_counts().sort_index()
    print("Distribuicao:")
    for n, c in dist2.items():
        print(f"  {n} ocorrencias do mesmo ID: {c} casos")
    print("\nExemplo:")
    ex_id = ids_dup_all.index[0]
    print(vias_all[vias_all["numero_ocorrencia_associado"] == ex_id][["numero_ocorrencia_associado", "ano_fato", "_ano_arquivo"] + cols_via].to_string())
