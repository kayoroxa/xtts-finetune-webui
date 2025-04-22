import os
import random
from pathlib import Path

import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Filtros
IGNORE_PREFIXES = ["segment_"]
MIN_DURATION_SECONDS = 10.0  # tempo mínimo em segundos para considerar o áudio

# Configurações
REFERENCE_FOLDER = Path(r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs")
TEXT = """
A indústria gananciosa dos cursinhos tradicionais dominou o nosso país a tal ponto que as pessoas nem conseguem acreditar que é possível aprender inglês rápido. Eles fizeram até mesmo muitas pessoas duvidarem de seus potenciais e se acharem incapazes de aprender uma nova língua. Mas, como eu falei, o problema nunca foi você nem eu, e sim o método usado aqui no Brasil.
""".strip()

LANG = "pt"

# Caminhos dos arquivos do modelo
READY = Path(r"E:\REPOS\xtts-finetune-webui\finetune_models\ready")
CONFIG_PATH = READY / "config.json"
CHECKPOINT_PATH = READY / "model.pth"
VOCAB_PATH = READY / "vocab.json"
SPEAKER_PATH = READY / "speakers_xtts.pth"

# Pasta de saída
OUT_DIR = Path("audios_gerados")
OUT_DIR.mkdir(exist_ok=True)

# Carrega o modelo
config = XttsConfig()
config.load_json(str(CONFIG_PATH))
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_path=str(CHECKPOINT_PATH), vocab_path=str(VOCAB_PATH), speaker_file_path=str(SPEAKER_PATH), use_deepspeed=False)
model.cuda()

# Geração dos áudios
for wav_file in REFERENCE_FOLDER.glob("*.wav"):
    base_name = wav_file.stem

    # Ignorar arquivos com prefixos indesejados
    if any(base_name.startswith(prefix) for prefix in IGNORE_PREFIXES):
        print(f"⏭️  Ignorando por prefixo: {wav_file.name}")
        continue

    # Verifica duração do áudio
    info = torchaudio.info(str(wav_file))
    duration_sec = info.num_frames / info.sample_rate
    if duration_sec < MIN_DURATION_SECONDS:
        print(f"⏭️  Ignorando por ser curto ({duration_sec:.2f}s): {wav_file.name}")
        continue

    unique_id = f"{random.randint(0, 999999):06}"
    output_name = f"{base_name}_{unique_id}.wav"
    output_path = OUT_DIR / output_name

    print(f"🔊 Gerando: {output_name}")

    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=str(wav_file),
        gpt_cond_len=model.config.gpt_cond_len,
        max_ref_length=model.config.max_ref_len,
        sound_norm_refs=model.config.sound_norm_refs
    )

    output = model.inference(
        text=TEXT,
        language=LANG,
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.75,
        length_penalty=1,
        repetition_penalty=5.0,
        top_k=50,
        top_p=0.85,
        enable_text_splitting=True
    )

    output_tensor = torch.tensor(output["wav"]).unsqueeze(0)
    torchaudio.save(str(output_path), output_tensor, 24000)

print("✅ Todos os áudios foram gerados com sucesso.")
