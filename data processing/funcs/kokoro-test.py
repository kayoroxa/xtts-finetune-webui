import os
import random

import pandas as pd
import soundfile as sf
from kokoro import KPipeline


# Função para gerar nome aleatório de 4 dígitos
def random_name():
    return str(random.randint(10000000, 99999999))

# Caminhos
input_csv = r'E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_eval.csv'
output_wav_folder = r'E:\REPOS\xtts-finetune-webui\finetune_models\dataset\kokoro-wavs'
output_csv = r'E:\REPOS\xtts-finetune-webui\finetune_models\dataset\metadata_eval_kokoro.csv'

# Garante que a pasta de saída existe
os.makedirs(output_wav_folder, exist_ok=True)

# Carrega o CSV original
df = pd.read_csv(input_csv, sep='|', names=['audio_file', 'text', 'speaker_name'])

# Inicializa o pipeline
pipeline = KPipeline(lang_code='p')

# Verifica se já existe um CSV anterior para continuar
if os.path.exists(output_csv):
    new_df = pd.read_csv(output_csv, sep='|', names=['audio_file', 'text', 'speaker_name'])
    frases_ja_processadas = set(new_df['text'].tolist())
else:
    new_df = pd.DataFrame(columns=['audio_file', 'text', 'speaker_name'])
    frases_ja_processadas = set()

# Loop para gerar os áudios
for idx, row in df.iterrows():
    text = row['text']

    if text in frases_ja_processadas:
        print(f'[{idx+1}/{len(df)}] Já processado, pulando: {text}')
        continue

    try:
        generator = pipeline(text, voice=r'E:/REPOS/script dark generator/tts/kokoro/pm_santa.pt')
        
        for i, (gs, ps, audio) in enumerate(generator):
            audio_name = f'{random_name()}.wav'
            audio_path = os.path.join(output_wav_folder, audio_name)
            sf.write(audio_path, audio, 24000)

            # Monta o novo registro
            new_row = pd.DataFrame([[f'kokoro-wavs/{audio_name}', text, 'kokoro']], 
                                   columns=['audio_file', 'text', 'speaker_name'])
            new_df = pd.concat([new_df, new_row], ignore_index=True)

            # Atualiza o set de frases já processadas
            frases_ja_processadas.add(text)

            # Salva incrementalmente
            new_df.to_csv(output_csv, sep='|', index=False, header=False)

            print(f'[{idx+1}/{len(df)}] Gerado e salvo: {audio_name}')
            
            break  # Sai do generator após o primeiro

    except Exception as e:
        print(f'Erro na linha {idx}: {e}')
        continue

print('Finalizado! CSV salvo em:', output_csv)
