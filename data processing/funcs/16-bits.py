import os

import librosa
import pandas as pd
import soundfile as sf

# Caminhos
caminho_metadata = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv"
pasta_wavs = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset"

# Carregar metadata
df = pd.read_csv(caminho_metadata, sep="|")

# Extrair os paths únicos
paths_unicos = df['audio_file'].unique()

total_arquivos = len(paths_unicos)
print(f"Total de arquivos únicos: {total_arquivos}")

# Parâmetros desejados
sample_rate_desejado = 22050
channels_desejado = 1
subtype_desejado = 'PCM_16'

for idx, relative_path in enumerate(paths_unicos):
    caminho_audio = os.path.join(pasta_wavs, relative_path)

    progresso = (idx + 1) / total_arquivos * 100
    print(f"[{progresso:.2f}%] Processando: {caminho_audio}")

    if not os.path.exists(caminho_audio):
        print(f"❌ Arquivo não encontrado: {caminho_audio}")
        continue

    try:
        # Ler header do áudio
        info = sf.info(caminho_audio)

        precisa_converter = False

        if info.samplerate != sample_rate_desejado:
            precisa_converter = True

        if info.channels != channels_desejado:
            precisa_converter = True

        if info.subtype != subtype_desejado:
            precisa_converter = True

        if not precisa_converter:
            print(f"✅ OK: {caminho_audio}")
            continue

        # Carregar áudio completo e converter
        audio, sr = librosa.load(caminho_audio, sr=sample_rate_desejado, mono=True)

        sf.write(
            caminho_audio,
            audio,
            samplerate=sample_rate_desejado,
            subtype=subtype_desejado
        )

        print(f"🔧 Convertido: {caminho_audio}")

    except Exception as e:
        print(f"❌ Erro ao processar {caminho_audio}: {e}")
