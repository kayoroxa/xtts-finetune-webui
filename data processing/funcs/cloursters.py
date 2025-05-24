import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torchaudio
import umap
from speechbrain.pretrained import EncoderClassifier

# === CONFIGURAÇÃO ===
# Caminho absoluto da pasta onde está o metadata
BASE_PATH = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset"
METADATA_CSV = os.path.join(BASE_PATH, "metadata_train.csv")

# === CARREGAR METADATA ===
df = pd.read_csv(METADATA_CSV, sep="|", names=["audio_file", "text", "speaker_name"])

# === MODELO DE EMBEDDING ===
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

embeddings = []
file_names = []

# === PROCESSAR ARQUIVOS ===
for idx, row in df.iterrows():
    audio_rel_path = row['audio_file']
    audio_abs_path = os.path.join(BASE_PATH, audio_rel_path)

    if os.path.isfile(audio_abs_path):
        try:
            signal, fs = torchaudio.load(audio_abs_path)
            embedding = classifier.encode_batch(signal)
            embeddings.append(embedding.squeeze().detach().numpy())
            file_names.append(audio_rel_path)
        except Exception as e:
            print(f"Erro no arquivo {audio_abs_path}: {e}")
    else:
        print(f"Arquivo não encontrado: {audio_abs_path}")

# === CONVERTER PARA ARRAY ===
embeddings = np.vstack(embeddings)

# === REDUÇÃO DE DIMENSÃO PARA VISUALIZAÇÃO ===
reducer = umap.UMAP()
embeddings_2d = reducer.fit_transform(embeddings)

# === PLOT ===
plt.figure(figsize=(10, 8))
plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], s=30)

for i, txt in enumerate(file_names):
    plt.annotate(txt, (embeddings_2d[i, 0], embeddings_2d[i, 1]), fontsize=7)

plt.title("Speaker Embedding Clustering - XTTS Dataset")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.show()
