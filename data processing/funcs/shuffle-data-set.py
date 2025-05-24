from pathlib import Path

import pandas as pd

# Caminho do arquivo CSV original
csv_path = Path(r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_train.csv")

# Carrega o CSV
df = pd.read_csv(csv_path, sep='|')

# Embaralha as linhas
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Salva sobrescrevendo o arquivo original
df_shuffled.to_csv(csv_path, sep='|', index=False)

print(f"Arquivo sobrescrito com linhas embaralhadas: {csv_path}")
