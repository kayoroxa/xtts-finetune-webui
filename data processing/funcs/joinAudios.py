import os

from pydub import AudioSegment

# Caminho da pasta com os áudios
pasta = "E:/REPOS/xtts-finetune-webui/finetune_models/dataset/wavs"
arquivos = sorted(os.listdir(pasta))  # organiza em ordem alfabética

print(f"Encontrados {len(arquivos)} arquivos na pasta.")

# 1 segundo de silêncio
silencio = AudioSegment.silent(duration=1000)

# Áudio final
audio_final = AudioSegment.empty()

for i, arquivo in enumerate(arquivos, start=1):
    if arquivo.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
        caminho_completo = os.path.join(pasta, arquivo)
        print(f"[{i}] Processando: {arquivo}")
        try:
            audio = AudioSegment.from_file(caminho_completo)
            audio_final += audio + silencio  # junta o áudio com 1s de silêncio
        except Exception as e:
            print(f"⚠️ Erro ao processar {arquivo}: {e}")

print("Finalizando exportação...")
# Exporta o resultado
saida = "audio_concatenado.mp3"
audio_final.export(saida, format="mp3")
print(f"✅ Arquivo final gerado: {saida}")
