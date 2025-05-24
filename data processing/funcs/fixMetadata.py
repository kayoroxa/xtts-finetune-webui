import os
import shutil

import pandas as pd

# Caminhos
caminho_metadata_eval = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_eval.csv"
caminho_metadata_train = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv"
pasta_wavs = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs"
pasta_bad_wavs = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\bad_wavs"

# Garante que a pasta de "bad_wavs" existe
os.makedirs(pasta_bad_wavs, exist_ok=True)

# -------------- LIMPAR O METADATA_EVAL --------------

# Carregar o CSV
df_eval = pd.read_csv(caminho_metadata_eval, sep="|")

# Número de linhas antes
linhas_antes = len(df_eval)

# Identificar linhas que contêm "..."
linhas_com_pontos = df_eval[df_eval['text'].str.contains(r'\.\.\.', na=False)]

# Identificar linhas que não terminam com ".", "!" ou "?"
linhas_final_errado = df_eval[~df_eval['text'].str.strip().str.endswith(('.', '!', '?'))]

# Unir todos os exemplos a serem removidos
linhas_para_remover = pd.concat([linhas_com_pontos, linhas_final_errado]).drop_duplicates()

# Agora removemos essas linhas do dataframe
df_eval_filtrado = df_eval.drop(linhas_para_remover.index)

# Número de linhas depois
linhas_depois = len(df_eval_filtrado)

# Calcular quantas linhas foram apagadas
linhas_apagadas = linhas_antes - linhas_depois

# Salvar sobrescrevendo o arquivo original
df_eval_filtrado.to_csv(caminho_metadata_eval, sep="|", index=False)

# Mostrar quantas linhas foram apagadas
print(f"{linhas_apagadas} linhas foram apagadas.")

# Mostrar exemplos de linhas apagadas
print("\nExemplos de frases removidas:")
for frase in linhas_para_remover['text']:
    print(frase)

# -------------- MOVER AUDIOS NÃO USADOS --------------

# Carregar o metadata_train também
df_train = pd.read_csv(caminho_metadata_train, sep="|")

# Criar um conjunto com todos os arquivos listados nos metadatas
audios_usados = set(df_train['audio_file'].apply(lambda x: os.path.basename(x)))
audios_usados.update(df_eval_filtrado['audio_file'].apply(lambda x: os.path.basename(x)))

# Percorrer a pasta dos WAVs
for arquivo in os.listdir(pasta_wavs):
    if arquivo.endswith(".wav"):
        if arquivo not in audios_usados:
            # mover o arquivo para pasta bad_wavs
            origem = os.path.join(pasta_wavs, arquivo)
            destino = os.path.join(pasta_bad_wavs, arquivo)
            shutil.move(origem, destino)
            print(f"Arquivo movido para bad_wavs: {arquivo}")
