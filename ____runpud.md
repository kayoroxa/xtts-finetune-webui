pip list
sudo apt update && sudo apt install -y unzip git wget
cd workspace
git clone https://github.com/daswer123/xtts-finetune-webui
cd xtts-finetune-webui
pip install -r requirements.txt --prefer-binary



rsync -avz -e "ssh -i /caminho/sua-chave.pem" "E:\REPOS\xtts-finetune-webui\finetune_models\dataset" user@ip_do_pod:/workspace/dataset/


pip install gdown
gdown https://drive.google.com/uc?id=ID_DO_SEU_DATASET
unzip dataset.zip
mv dataset finetuning/dataset

python xtts_demo.py
porta: 5003

tensorboard --logdir="\finetune_models\run\training"
porta: 6006