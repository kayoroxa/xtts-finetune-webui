import os
import random

import pandas as pd
import soundfile as sf
from audiomentations import AddGaussianNoise, Compose, PitchShift, TimeStretch
from tqdm import tqdm

# ─── CONFIGURAÇÕES ──────────────────────────────────────────────────────────────
INPUT_DIR = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs"
OUTPUT_DIR = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\wavs_augmented"
METADATA_CSV = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv"
CSV_SEP = "|"
CSV_COLS = ["file", "text", "speaker"]

# Augmentações ativas e quantidade por arquivo
ACTIVE_AUGMENTS = ['noise']  # opções: 'noise', 'pitch', 'stretch'
NUM_AUGMENTS = 1

# Transformações disponíveis
AVAILABLE_AUGMENTATIONS = {
    'noise': Compose([AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.003, p=1.0)]),
    'pitch': Compose([PitchShift(min_semitones=-1, max_semitones=1, p=1.0)]),
    'stretch': Compose([TimeStretch(min_rate=0.97, max_rate=1.03, p=1.0)]),
}

AUG_SUFFIXES = [f"_{key}.wav" for key in AVAILABLE_AUGMENTATIONS]

# ─── FUNÇÕES ─────────────────────────────────────────────────────────────────────

def load_metadata(path: str) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Metadata não encontrado: {path}")
    df = pd.read_csv(path, sep=CSV_SEP, header=None, names=CSV_COLS, dtype=str)
    df = df.dropna(subset=["file", "text"])
    return df.drop_duplicates(subset=CSV_COLS, keep="first")


def safe_write_metadata(df: pd.DataFrame, path: str):
    backup = path + ".bak"
    os.replace(path, backup)
    try:
        df.to_csv(path, sep=CSV_SEP, header=False, index=False)
        os.remove(backup)
    except Exception as e:
        os.replace(backup, path)
        raise RuntimeError(f"Falha ao salvar metadata; backup restaurado. Erro: {e}")


def resolve_wav_path(name_in_metadata: str) -> str:
    filename = os.path.basename(name_in_metadata)
    for folder in (INPUT_DIR, OUTPUT_DIR):
        candidate = os.path.join(folder, filename)
        if os.path.isfile(candidate):
            return candidate
    return None


def is_augmented(name: str) -> bool:
    basename = os.path.basename(name)
    return any(basename.endswith(suffix) for suffix in AUG_SUFFIXES)

# ─── FLUXO PRINCIPAL ───────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_meta = load_metadata(METADATA_CSV)

    # 1) Limpar metadata de entradas augmentadas antigas
    df_clean = df_meta[~df_meta['file'].apply(is_augmented)].copy()

    # 2) Apagar arquivos augmentados antigos em ambos diretórios
    for folder in (INPUT_DIR, OUTPUT_DIR):
        for fname in os.listdir(folder):
            if is_augmented(fname):
                try:
                    os.remove(os.path.join(folder, fname))
                    print(f"[DEL] {fname}")
                except:
                    pass

    # 3) Gerar novos augments somente a partir de df_clean
    new_rows = []
    for _, row in tqdm(df_clean.iterrows(), total=len(df_clean), desc="Augmenting"):
        name_in_metadata = row['file']
        wav_path = resolve_wav_path(name_in_metadata)
        if not wav_path:
            tqdm.write(f"[SKIP] WAV não encontrado: {name_in_metadata}")
            continue
        samples, sr = sf.read(wav_path)
        base_name = os.path.splitext(os.path.basename(wav_path))[0]

        # Seleciona aleatoriamente as augmentações
        choices = random.choices(ACTIVE_AUGMENTS, k=NUM_AUGMENTS)
        for idx, key in enumerate(choices, 1):
            aug = AVAILABLE_AUGMENTATIONS[key]
            new_name = f"{base_name}_{key}.wav"
            out_path = os.path.join(OUTPUT_DIR, new_name)
            if os.path.isfile(out_path):
                continue
            augmented = aug(samples=samples, sample_rate=sr)
            sf.write(out_path, augmented, sr)
            new_rows.append([new_name, row['text'], row['speaker']])

    if not new_rows:
        print("ℹ️ Nenhum novo arquivo gerado.")
        return

    # 4) Atualizar metadata com originais + novos
    df_new = pd.DataFrame(new_rows, columns=CSV_COLS)
    df_final = pd.concat([df_clean, df_new], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=CSV_COLS, keep="first")
    safe_write_metadata(df_final, METADATA_CSV)
    print(f"✅ Augmentação concluída. {len(new_rows)} novos arquivos adicionados.")

if __name__ == "__main__":
    main()