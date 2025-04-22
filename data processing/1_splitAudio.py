# data processing/1_splitAudio.py
import os
from pathlib import Path

from pydub import AudioSegment, silence

print("Let's go!")
# Diretório base (mesmo onde o script está)
BASE_DIR = Path(__file__).resolve().parent

# Caminhos
arquivo = Path("C:/Users/Fernandes/Music/treino IA VOZ/16-04/_tts6.wav")
output_dir = BASE_DIR / "wavs"
output_dir.mkdir(exist_ok=True)

# Parâmetros de corte
limite_silencio_db = -38  # silêncios abaixo disso serão ignorados
duracao_minima_voz_ms = 400  # duração mínima de um trecho de voz válido
padding_ms = 200  # adicionar um pouco de silêncio antes/depois para evitar cortes abruptos
fim_padding_ms = 400  # adicionar um pouco de silêncio antes/depois para evitar cortes abruptos
nome_base = arquivo.stem

# Carrega o áudio
audio = AudioSegment.from_file(arquivo)

# Converte para mono (por segurança)
audio = audio.set_channels(1)

# Detecta trechos que não são silêncio
# Aumentei min_silence_len para 1000ms para detectar silêncios mais longos
intervalos = silence.detect_nonsilent(audio, 
                                      min_silence_len=1000,  # agora detecta silêncios de pelo menos 1s
                                      silence_thresh=limite_silencio_db,
                                      seek_step=1)

# Filtra intervalos muito curtos (ex: estalos)
intervalos_filtrados = []
for inicio, fim in intervalos:
    # Ainda aplicando filtro de duração mínima
    if fim - inicio >= duracao_minima_voz_ms:
        # Soma padding ao início e fim, garantindo que não ultrapasse os limites do áudio
        inicio_pad = max(0, inicio - padding_ms)
        fim_pad = min(len(audio), fim + fim_padding_ms)
        intervalos_filtrados.append((inicio_pad, fim_pad))

# Exporta os trechos cortados
for i, (inicio, fim) in enumerate(intervalos_filtrados):
    trecho = audio[inicio:fim]
    nome_saida = output_dir / f"{nome_base}_{i+1:05d}.wav"
    trecho.export(nome_saida, format="wav")
    print(f"Exportado: {nome_saida}")