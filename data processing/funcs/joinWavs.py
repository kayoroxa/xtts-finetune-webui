import os
import re
from collections import defaultdict

from pydub import AudioSegment

# Caminho da pasta com os áudios
audio_dir = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs"  # <- Altere para o caminho correto
output_dir = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavsJoin"

# Duração do silêncio em milissegundos
silencio = AudioSegment.silent(duration=500)

# Regex para extrair prefixo (ex: "_tts6_" de "_tts6_00123.wav")
prefixo_regex = re.compile(r"^(.+?)(\d+)\.wav$")

# Agrupar arquivos por prefixo
grupos = defaultdict(list)

for arquivo in os.listdir(audio_dir):
    if arquivo.endswith(".wav"):
        match = prefixo_regex.match(arquivo)
        if match:
            prefixo, numero = match.groups()
            grupos[prefixo].append((int(numero), arquivo))

# Filtrar grupos com mais de 30 arquivos e processar
for prefixo, arquivos in grupos.items():
    if len(arquivos) >= 30:
        arquivos.sort()  # Ordena pela parte numérica
        combinado = AudioSegment.empty()
        for _, nome_arquivo in arquivos:
            caminho = os.path.join(audio_dir, nome_arquivo)
            audio = AudioSegment.from_wav(caminho)
            combinado += audio + silencio
        # Salvar o resultado
        nome_saida = f"{prefixo.strip('_')}_combinado.wav"
        combinado.export(os.path.join(output_dir, nome_saida), format="wav")
        print(f"Arquivo salvo: {nome_saida}")
