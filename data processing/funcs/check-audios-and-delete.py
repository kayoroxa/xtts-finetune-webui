import json
import os
import sys
import time

import keyboard
import pandas as pd
import pygame

# Caminhos
pasta_base = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset"
caminho_csv = os.path.join(pasta_base, "metadata_train.csv")
caminho_progresso = r"E:\REPOS\xtts-finetune-webui\finetune_models\dataset\funcs\catalogo_progresso.json"

# 🎯 FILTROS de nome dos áudios (ex: ["segment_", "intro", "teste"])
filtros_nome_audio = ["ele-"]  # Deixe vazio [] para tocar todos

# Inicializa o pygame
pygame.mixer.init()

# Carrega o CSV
df_original = pd.read_csv(caminho_csv, sep="|")

# Carrega progresso anterior ou cria um novo
if os.path.exists(caminho_progresso):
    with open(caminho_progresso, "r") as f:
        audios_processados = set(json.load(f))
else:
    audios_processados = set()

# Verifica se todos os arquivos listados existem
def verificar_audios_existentes(df):
    faltando = []
    for i, row in df.iterrows():
        caminho_absoluto = os.path.join(pasta_base, row['audio_file'])
        if not os.path.isfile(caminho_absoluto):
            faltando.append((i, row['audio_file']))
    return faltando

# Filtra por nome e por progresso (apenas na inicialização)
def filtrar_indices_por_nome(df, filtros):
    if not filtros:
        filtrados = df
    else:
        filtrados = df[df['audio_file'].apply(lambda nome: any(f in nome for f in filtros))]

    # Filtrar os que não estão no progresso
    filtrados = filtrados[~filtrados['audio_file'].isin(audios_processados)]
    return filtrados.index.tolist()

def tocar_audio(caminho):
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play()

def parar_audio():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

def deletar_audio(caminho, idx_original):
    parar_audio()
    os.remove(caminho)
    global df_original
    df_original.drop(index=idx_original, inplace=True)
    df_original.to_csv(caminho_csv, sep="|", index=False)
    df_original.reset_index(drop=True, inplace=True)

def salvar_progresso():
    with open(caminho_progresso, "w") as f:
        json.dump(list(audios_processados), f)

def main():
    faltando = verificar_audios_existentes(df_original)
    if faltando:
        print("⚠️ Os seguintes arquivos estão listados no CSV mas não existem no disco:\n")
        for idx, caminho in faltando:
            print(f"[Linha {idx + 1}] Arquivo não encontrado: {caminho}")
        print("\nCorrija os arquivos antes de continuar.")
        sys.exit()

    indices_filtrados = filtrar_indices_por_nome(df_original, filtros_nome_audio)
    if not indices_filtrados:
        print("Nenhum áudio encontrado com os filtros especificados ou já processados.")
        return

    idx_visual = 0
    print("Controles: [Enter] tocar/parar, [Delete] deletar e próximo, [↓] próximo (marca como verificado), [↑] anterior, [Esc] sair.\n")

    while idx_visual < len(indices_filtrados):
        idx_original = indices_filtrados[idx_visual]
        linha = df_original.loc[idx_original]
        caminho_relativo = linha['audio_file']
        caminho_absoluto = os.path.join(pasta_base, caminho_relativo)

        print(f"[{idx_visual + 1}/{len(indices_filtrados)}] Tocando: {caminho_relativo}")
        tocar_audio(caminho_absoluto)

        while True:
            time.sleep(0.1)

            if keyboard.is_pressed('enter'):
                parar_audio()
                tocar_audio(caminho_absoluto)
                while keyboard.is_pressed('enter'): pass

            elif keyboard.is_pressed('*'):
                print(f"❌ Deletando: {caminho_relativo}")
                deletar_audio(caminho_absoluto, idx_original)

                # Se deletou, garante que não fique no progresso
                audios_processados.discard(caminho_relativo)

                # Atualiza os índices depois de deletar
                indices_filtrados = filtrar_indices_por_nome(df_original, filtros_nome_audio)

                if idx_visual >= len(indices_filtrados):
                    idx_visual = max(0, len(indices_filtrados) - 1)
                salvar_progresso()
                break

            elif keyboard.is_pressed('down'):
                parar_audio()
                audios_processados.add(caminho_relativo)  # Marca como verificado
                salvar_progresso()
                idx_visual += 1
                if idx_visual >= len(indices_filtrados):
                    print("\nFim da lista.")
                    sys.exit()
                break

            elif keyboard.is_pressed('up'):
                parar_audio()
                idx_visual = max(0, idx_visual - 1)
                break

    salvar_progresso()
    print("\nTodos os áudios foram processados.")

if __name__ == "__main__":
    main()