import csv
import shutil
from pathlib import Path

import torch
from faster_whisper import WhisperModel

# Diretório base (onde o script está)
BASE_DIR = Path(__file__).resolve().parent

# --- Configurações ---
PASTA_CORTES          = BASE_DIR / "wavs"
BAD_WAVS_DIR          = BASE_DIR / "bad_wavs"
METADATA_CSV          = BASE_DIR / "metadata.csv"
WHISPER_MODEL_NAME    = "large-v3"
SPEAKER_NAME          = "coqui"
ARQUIVO_PREFIX        = "_tts6"

# Novas variáveis para verificação de confiança
CHECK_CONFIDENCE      = True      # True para filtrar áudios de baixa confiança
CONFIDENCE_THRESHOLD  = -0.21     # Média de avg_logprob mínima aceitável

# Verifica se a pasta de cortes existe
if not PASTA_CORTES.exists():
    print(f"Pasta de cortes não encontrada: {PASTA_CORTES}")
    exit(1)

# Carrega o modelo Whisper
print(f"Carregando modelo Whisper: {WHISPER_MODEL_NAME}")
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if torch.cuda.is_available() else "int8"
model = WhisperModel(WHISPER_MODEL_NAME, device=device, compute_type=compute_type)
print("✅ Modelo carregado.\n")

# Lista os arquivos .wav com prefixo definido
arquivos_wav = sorted(PASTA_CORTES.glob(f"{ARQUIVO_PREFIX}*.wav"))
if not arquivos_wav:
    print("❌ Nenhum arquivo .wav que começa com:", ARQUIVO_PREFIX)
    exit(1)

# Decide se escrevemos o cabeçalho
novo_arquivo = not METADATA_CSV.exists()

with open(METADATA_CSV, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    if novo_arquivo:
        writer.writerow(["audio_file", "text", "speaker_name"])

    for i, arquivo in enumerate(arquivos_wav, 1):
        print(f"[{i}/{len(arquivos_wav)}] Transcrevendo: {arquivo.name}")
        try:
            segments, _ = model.transcribe(
                str(arquivo),
                language="pt"
            )
            segments = list(segments)
            # Calcula confiança média
            if segments:
                avg_logprobs = [seg.avg_logprob for seg in segments if hasattr(seg, "avg_logprob")]
                media_logprob = sum(avg_logprobs) / len(avg_logprobs)
                print(f"🔎 Confiança média (avg_logprob): {media_logprob:.2f}")

                # Se estiver abaixo do limiar, move para bad_wavs e pula
                if CHECK_CONFIDENCE and media_logprob < CONFIDENCE_THRESHOLD:
                    print(f"⚠️ Ignorando {arquivo.name} por baixa confiança (limiar={CONFIDENCE_THRESHOLD})")
                    BAD_WAVS_DIR.mkdir(parents=True, exist_ok=True)
                    destino = BAD_WAVS_DIR / arquivo.name
                    shutil.move(str(arquivo), str(destino))
                    print(f"📁 Movido para: {destino}")
                    continue

            # Junta todos os textos
            textos = [seg.text.strip() for seg in segments if seg.text.strip()]
            texto_completo = " ".join(textos)

            if texto_completo:
                writer.writerow([f"wavs/{arquivo.name}", texto_completo, SPEAKER_NAME])

        except Exception as e:
            print(f"⚠️ Erro ao transcrever {arquivo.name}: {e}")

print(f"\n✅ Transcrição concluída e salva em: {METADATA_CSV.resolve()}")
