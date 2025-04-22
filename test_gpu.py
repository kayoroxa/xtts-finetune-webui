import torch

print("CUDA disponível:", torch.cuda.is_available())
print("cuDNN disponível:", torch.backends.cudnn.is_available())
print("Versão do cuDNN:", torch.backends.cudnn.version())
