# data processing/1_splitAudio.py
# arquivo = Path("C:/Users/Fernandes/Music/treino IA VOZ/16-04/_tts6.wav")
# data processing/1_splitAudio.py
import os
import time
from pathlib import Path

from pydub import AudioSegment, silence

print("🎬 Let's go!")
start_time = time.time()

# Diretório base
BASE_DIR = Path(__file__).resolve().parent

# Caminhos
arquivo = Path("C:/Users/Fernandes/Music/treino IA VOZ/16-04/_tts6.wav")
# arquivo = Path("E:/REPOS/AI LAB/alinha text audio/sutil arte de ligar o foda-se.wav")
output_dir = BASE_DIR / "wavs"
output_dir.mkdir(exist_ok=True)

# Parâmetros
limite_silencio_db = -38
duracao_minima_voz_ms = 400
padding_ms = 200
fim_padding_ms = 400
nome_base = arquivo.stem

print(f"📂 Carregando áudio: {arquivo.name}")
audio = AudioSegment.from_file(arquivo).set_channels(1)
duracao_audio = len(audio)
print(f"⏱️ Duração total: {duracao_audio / 1000:.2f} segundos")

# Detectar partes não silenciosas (manual, mostrando progresso)
print("🔍 Detectando trechos de voz...")

step = 300_000  # 5 minutos (em milissegundos)
intervalos = []
inicio = 0

while inicio < duracao_audio:
    fim = min(inicio + step, duracao_audio)
    trecho = audio[inicio:fim]
    partes = silence.detect_nonsilent(trecho,
                                       min_silence_len=1000,
                                       silence_thresh=limite_silencio_db,
                                       seek_step=1)
    for part in partes:
        intervalo_absoluto = (part[0] + inicio, part[1] + inicio)
        intervalos.append(intervalo_absoluto)

    progresso = (fim / duracao_audio) * 100
    print(f"🛠️ Analisado: {fim/1000:.0f}s / {duracao_audio/1000:.0f}s ({progresso:.2f}%)", end='\r')
    inicio = fim

print(f"\n🔎 {len(intervalos)} intervalos detectados")

# Filtrar trechos curtos
intervalos_filtrados = []
for inicio, fim in intervalos:
    if fim - inicio >= duracao_minima_voz_ms:
        inicio_pad = max(0, inicio - padding_ms)
        fim_pad = min(duracao_audio, fim + fim_padding_ms)
        intervalos_filtrados.append((inicio_pad, fim_pad))

print(f"✅ {len(intervalos_filtrados)} trechos após filtragem\n")

# Exportar trechos com barra de progresso leve
total = len(intervalos_filtrados)
print(f"📤 Iniciando exportação de {total} trechos para: {output_dir}\n")

for i, (inicio, fim) in enumerate(intervalos_filtrados, 1):
    trecho = audio[inicio:fim]
    nome_saida = output_dir / f"{nome_base}_{i:05d}.wav"
    trecho.export(nome_saida, format="wav")

    if i % max(1, total // 50) == 0 or i == total:
        porcentagem = (i / total) * 100
        print(f"📦 Progresso: [{i}/{total}] - {porcentagem:6.2f}%", end='\r')

elapsed = time.time() - start_time
print(f"\n\n🏁 Finalizado! Tempo total: {elapsed:.2f} segundos")
