@echo off
echo === Etapa 1: Executando 1_splitAudio.py (fora do venv) ===
python 1_splitAudio.py

echo.
echo === Ativando ambiente virtual (venv) ===
CALL venv\Scripts\activate.bat

echo === Etapa 2: Executando 2_whisperAudios.py (com venv) ===
python 2_whisperAudios.py

echo.
echo ✅ Processamento concluído.
pause
