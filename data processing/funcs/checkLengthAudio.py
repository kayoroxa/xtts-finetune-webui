import os

import pandas as pd
import soundfile as sf

# Caminhos
caminho_metadata = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv"
pasta_wavs = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset"

# Carregar o CSV
df = pd.read_csv(caminho_metadata, sep="|")

# Verificar textos com mais de 200 caracteres
df_long_texts = df[df['text'].str.len() > 200]
qnt_long_texts = len(df_long_texts)

print(f"Textos com mais de 200 caracteres: {qnt_long_texts}")

if qnt_long_texts > 0:
    print(df_long_texts[['audio_file', 'text']])

# Inicializar variável de tempo total
duracao_total_segundos = 0
qnt_files_not_found = 0

# Para cada linha do metadata
for arquivo_wav in df['audio_file']:
    caminho_completo = os.path.join(pasta_wavs, arquivo_wav)
    
    # Verificar se o arquivo existe
    if os.path.exists(caminho_completo):
        # Carrega apenas as informações de duração
        info = sf.info(caminho_completo)
        duracao_total_segundos += info.duration
    else:
        qnt_files_not_found += 1
        print(f"Arquivo não encontrado: {caminho_completo}")

print(f"Qnt arquivos nao encontrados: {qnt_files_not_found}")

# Calcular duração em minutos
duracao_total_minutos = duracao_total_segundos / 60

# Mostrar o resultado
print(f"Tempo total de áudio: {duracao_total_segundos:.2f} segundos")
print(f"Tempo total de áudio: {duracao_total_minutos:.2f} minutos")
