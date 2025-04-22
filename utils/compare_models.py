import hashlib

import torch


def carregar_modelo(path):
    try:
        return torch.load(path, map_location='cpu', weights_only=True)

    except Exception as e:
        print(f"Erro ao carregar {path}: {e}")
        return None

def hash_modelo(state_dict):
    m = hashlib.sha256()
    for key in sorted(state_dict.keys()):
        valor = state_dict[key]
        if isinstance(valor, torch.Tensor):
            m.update(valor.detach().cpu().flatten().numpy().tobytes())
        else:
            # Opcional: inclui tipo e string do valor não tensor (ou ignora totalmente)
            m.update(str(valor).encode('utf-8'))
    return m.hexdigest()


def comparar_modelos(path1, path2):
    modelo1 = carregar_modelo(path1)
    modelo2 = carregar_modelo(path2)

    if modelo1 is None or modelo2 is None:
        print("Não foi possível carregar um ou ambos os modelos.")
        return

    # Se forem modelos salvos com torch.save(model.state_dict())
    if isinstance(modelo1, dict) and isinstance(modelo2, dict):
        hash1 = hash_modelo(modelo1)
        hash2 = hash_modelo(modelo2)

        if hash1 == hash2:
            print("✅ Os modelos são IGUAIS!")
        else:
            print("❌ Os modelos são DIFERENTES.")
    else:
        print("⚠️ Um ou ambos os arquivos não parecem ser state_dict. Verifique como os modelos foram salvos.")

# Exemplo de uso
comparar_modelos('E:/REPOS/xtts-finetune-webui/finetune_models/run/training/GPT_XTTS_FT-April-17-2025_01+17AM-abe1201/best_model.pth', 'E:/REPOS/xtts-finetune-webui/finetune_models/run/training/GPT_XTTS_FT-April-17-2025_01+17AM-abe1201/best_model_5607.pth')
