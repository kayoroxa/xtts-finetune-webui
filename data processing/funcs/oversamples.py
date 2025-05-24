import re

import pandas as pd


def oversample_metadata(
    file_path: str,
    patterns: list[str],
    duplicate: int = 3,
    separator: str = '|'
):
    print(f"\n--- Carregando arquivo: {file_path} ---")
    df = pd.read_csv(file_path, header=None, sep=separator)
    print(f"Linhas carregadas: {len(df)}")

    print("\n--- Removendo duplicatas ---")
    df = df.drop_duplicates()
    print(f"Linhas após remoção de duplicatas: {len(df)}")

    if (duplicate == 0):
        print("\n⚠️ Nenhuma duplicata foi adicionada!")
        
        print(f"\n--- Salvando arquivo sobrescrevendo {file_path} ---")
        df.to_csv(file_path, header=False, index=False, sep=separator)
        print("✅ Arquivo salvo com sucesso.")
        return

    print("\n--- Aplicando padrões de oversample ---")
    total_matches = 0
    all_matches = []
    for pattern in patterns:
        print(f"\n> Verificando padrão: '{pattern}'")
        matched_rows = df[df[0].str.contains(pattern, flags=re.IGNORECASE, regex=True)]
        match_count = len(matched_rows)
        print(f"Linhas encontradas: {match_count}")
        if match_count > 0:
            print("Exemplos:")
            print(matched_rows.head(min(3, match_count)).to_string(index=False, header=False))
        total_matches += match_count
        all_matches.append(matched_rows)

    if total_matches == 0:
        print("\n⚠️ Nenhuma linha encontrada com os padrões fornecidos!")

    matches = pd.concat(all_matches * duplicate, ignore_index=True)

    print(f"\nLinhas adicionadas via oversample: {len(matches)} (x{duplicate})")

    print("\n--- Concatenando dataset final ---")
    df_final = pd.concat([df, matches], ignore_index=True)
    print(f"Total final de linhas antes do shuffle: {len(df_final)}")

    print("\n--- Embaralhando linhas (shuffle) ---")
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    print("Shuffle concluído.")

    print(f"\n--- Salvando arquivo sobrescrevendo {file_path} ---")
    df_final.to_csv(file_path, header=False, index=False, sep=separator)
    print("✅ Arquivo salvo com sucesso.")


# ---------- CONFIGURAÇÃO ----------
file_path = r'E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv'

patterns = """
wavs/5-1
wavs/18-5-e
""".strip().split('\n')

duplicate = 0

# ---------- EXECUTAR ----------
oversample_metadata(file_path, patterns, duplicate)
