import os
import random
from pathlib import Path

import torch
import torchaudio
from pydub import AudioSegment
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# CONFIGURAÇÕES BÁSICAS
LANG = "pt"
REFERENCE_FOLDER = Path(r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs")
READY = Path(r"E:\REPOS\xtts-finetune-webui\finetune_models\ready")
CONFIG_PATH = READY / "config.json"
CHECKPOINT_PATH = READY / "model.pth"
VOCAB_PATH = READY / "vocab.json"
SPEAKER_PATH = READY / "speakers_xtts.pth"
OUT_DIR = Path("audios_sentences")
OUT_DIR.mkdir(exist_ok=True)

# FRASES A SEREM USADAS
sentences = """
Inglês abre portas no trabalho.

Fluência garante melhores oportunidades.

Não saber inglês é limitante.

Estude todos os dias um pouco.

Pratique com filmes e músicas.

Cursinhos tradicionais atrasam o aprendizado.

Gramática demais trava sua fala.

Aprender inglês pode ser rápido.

Você não está sozinho nisso.

É possível aprender em semanas.

O mercado exige inglês fluente.

Método certo acelera o aprendizado.

Fale, ouça, leia e escreva.

Aprenda como uma criança aprende.

Famosos não usam métodos tradicionais.

Evite o ciclo do fracasso.

Seu cérebro aprende com contexto.

Assista filmes sem legenda hoje.

Você pode sim aprender inglês.

Decida mudar sua vida agora.
""".replace("\n\n", "\n").strip().split("\n")

# NOMES BASE DOS ARQUIVOS DE REFERÊNCIA (sem extensão)
REFERENCE_FILES = ["TTS_EDITRAW_1_00002", "_tts5_00042"]

# Carrega modelo
config = XttsConfig()
config.load_json(str(CONFIG_PATH))
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_path=str(CHECKPOINT_PATH), vocab_path=str(VOCAB_PATH), speaker_file_path=str(SPEAKER_PATH), use_deepspeed=False)
model.cuda()

# Geração para cada frase e referência
for ref_name in REFERENCE_FILES:
    ref_path = REFERENCE_FOLDER / f"{ref_name}.wav"
    if not ref_path.exists():
        print(f"❌ Arquivo não encontrado: {ref_path}")
        continue

    print(f"🎙️ Referência: {ref_name}")

    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=str(ref_path),
        gpt_cond_len=model.config.gpt_cond_len,
        max_ref_length=model.config.max_ref_len,
        sound_norm_refs=model.config.sound_norm_refs
    )

    for i, sentence in enumerate(sentences, 1):
        sentence_clean = sentence.strip()
        if not sentence_clean:
            continue

        print(f"📝 Frase {i}: {sentence_clean}")

        output = model.inference(
            text=sentence_clean,
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

        unique_id = f"{random.randint(0, 999999):06}"
        filename_base = f"{ref_name}_s{i}_{unique_id}"
        wav_path = OUT_DIR / f"{filename_base}.wav"
        mp3_path = OUT_DIR / f"{filename_base}.mp3"

        output_tensor = torch.tensor(output["wav"]).unsqueeze(0)
        torchaudio.save(str(wav_path), output_tensor, 24000)

        # Converter para MP3
        audio = AudioSegment.from_wav(str(wav_path))
        audio.export(str(mp3_path), format="mp3")
        os.remove(wav_path)  # remove o wav

print("✅ Fim da geração.")
