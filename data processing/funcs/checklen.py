import os

from pydub import AudioSegment

# Caminho da pasta com os áudios
pasta = r"C:\Users\Fernandes\Downloads\Telegram Desktop\ChatExport_2025-04-28\voice_messages"

# Extensões comuns de áudio do Telegram
extensoes_validas = ('.ogg', '.mp3', '.wav', '.m4a')

duracao_total_ms = 0

for arquivo in os.listdir(pasta):
    if arquivo.lower().endswith(extensoes_validas):
        caminho_completo = os.path.join(pasta, arquivo)
        try:
            audio = AudioSegment.from_file(caminho_completo)
            duracao_total_ms += len(audio)
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")

# Convertendo de milissegundos para minutos
duracao_total_min = duracao_total_ms / 1000 / 60

print(f"Duração total dos áudios: {duracao_total_min:.2f} minutos")
