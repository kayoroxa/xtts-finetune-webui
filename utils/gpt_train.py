import gc
import logging
import os
import shutil
from pathlib import Path

import torch
import torchaudio
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import (GPTArgs, GPTTrainer,
                                                     GPTTrainerConfig,
                                                     XttsAudioConfig)
from TTS.utils.manage import ModelManager


def generate_sample(model, config, text, ref_audio, lang, step):
    if not os.path.exists(ref_audio):
        print("[!] Áudio de referência não encontrado")
        return
    gpt_latent, speaker_embed = model.get_conditioning_latents(audio_path=ref_audio)
    out = model.inference(
        text=text,
        language=lang,
        gpt_cond_latent=gpt_latent,
        speaker_embedding=speaker_embed,
        temperature=config.audio.temperature,
        length_penalty=config.audio.length_penalty,
        repetition_penalty=config.audio.repetition_penalty,
        top_k=config.audio.top_k,
        top_p=config.audio.top_p,
        enable_text_splitting=True,
    )
    out_path = os.path.join(config.output_path, f"sample_epoch_{step}.wav")
    torchaudio.save(out_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
    print(f"[✓] Amostra salva: {out_path}")




def train_gpt(custom_model,version, language, num_epochs, batch_size, grad_acumm, train_csv, eval_csv, output_path, max_audio_length=255995, dropout_rate=0.0):
    #  Logging parameters
    RUN_NAME = "GPT_XTTS_FT"
    PROJECT_NAME = "XTTS_trainer"
    DASHBOARD_LOGGER = "tensorboard"
    LOGGER_URI = None

    # print(f"XTTS version = {version}")

    # Set here the path that the checkpoints will be saved. Default: ./run/training/
    OUT_PATH = os.path.join(output_path, "run", "training")

    # Training Parameters
    OPTIMIZER_WD_ONLY_ON_WEIGHTS = True  # for multi-gpu training please make it False
    START_WITH_EVAL = True  # if True it will star with evaluation
    BATCH_SIZE = batch_size  # set here the batch size
    GRAD_ACUMM_STEPS = grad_acumm  # set here the grad accumulation steps


    # Define here the dataset that you want to use for the fine-tuning on.
    config_dataset = BaseDatasetConfig(
        formatter="coqui",
        dataset_name="ft_dataset",
        path=os.path.dirname(train_csv),
        meta_file_train=train_csv,
        meta_file_val=eval_csv,
        language=language,
    )

    # Add here the configs of the datasets
    DATASETS_CONFIG_LIST = [config_dataset]

    # Define the path where XTTS v2.0.1 files will be downloaded
    CHECKPOINTS_OUT_PATH = os.path.join(Path.cwd(), "base_models",f"{version}")
    os.makedirs(CHECKPOINTS_OUT_PATH, exist_ok=True)


    # DVAE files
    DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth"
    MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth"

    # Set the path to the downloaded files
    DVAE_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(DVAE_CHECKPOINT_LINK))
    MEL_NORM_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(MEL_NORM_LINK))

    # download DVAE files if needed
    if not os.path.isfile(DVAE_CHECKPOINT) or not os.path.isfile(MEL_NORM_FILE):
        print(" > Downloading DVAE files!")
        ModelManager._download_model_files([MEL_NORM_LINK, DVAE_CHECKPOINT_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True)


    # Download XTTS v2.0 checkpoint if needed
    TOKENIZER_FILE_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/{version}/vocab.json"
    XTTS_CHECKPOINT_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/{version}/model.pth"
    XTTS_CONFIG_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/{version}/config.json"
    XTTS_SPEAKER_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/speakers_xtts.pth"

    # XTTS transfer learning parameters: You we need to provide the paths of XTTS model checkpoint that you want to do the fine tuning.
    TOKENIZER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(TOKENIZER_FILE_LINK))  # vocab.json file
    XTTS_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CHECKPOINT_LINK))  # model.pth file
    XTTS_CONFIG_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CONFIG_LINK))  # config.json file
    XTTS_SPEAKER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_SPEAKER_LINK))  # speakers_xtts.pth file

    # download XTTS v2.0 files if needed
    if not os.path.isfile(TOKENIZER_FILE) or not os.path.isfile(XTTS_CHECKPOINT):
        print(f" > Downloading XTTS v{version} files!")
        ModelManager._download_model_files(
            [TOKENIZER_FILE_LINK, XTTS_CHECKPOINT_LINK, XTTS_CONFIG_LINK,XTTS_SPEAKER_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True
        )

    # Transfer this files to ready folder
    READY_MODEL_PATH = os.path.join(output_path,"ready")
    if not os.path.exists(READY_MODEL_PATH):
        os.makedirs(READY_MODEL_PATH)

    NEW_TOKENIZER_FILE = os.path.join(READY_MODEL_PATH, "vocab.json")
    # NEW_XTTS_CHECKPOINT = os.path.join(READY_MODEL_PATH, "model.pth")
    NEW_XTTS_CONFIG_FILE = os.path.join(READY_MODEL_PATH, "config.json")
    NEW_XTTS_SPEAKER_FILE = os.path.join(READY_MODEL_PATH, "speakers_xtts.pth")

    shutil.copy(TOKENIZER_FILE, NEW_TOKENIZER_FILE)
    # shutil.copy(XTTS_CHECKPOINT, os.path.join(READY_MODEL_PATH, "model.pth"))
    shutil.copy(XTTS_CONFIG_FILE, NEW_XTTS_CONFIG_FILE)
    shutil.copy(XTTS_SPEAKER_FILE, NEW_XTTS_SPEAKER_FILE)

# Use from ready folder
    TOKENIZER_FILE = NEW_TOKENIZER_FILE # vocab.json file
    # XTTS_CHECKPOINT = NEW_XTTS_CHECKPOINT  # model.pth file
    XTTS_CONFIG_FILE = NEW_XTTS_CONFIG_FILE  # config.json file
    XTTS_SPEAKER_FILE = NEW_XTTS_SPEAKER_FILE  # speakers_xtts.pth file


    if custom_model != "":
        if os.path.exists(custom_model) and custom_model.endswith('.pth'):
            XTTS_CHECKPOINT = custom_model
            print(f" > Loading custom model: {XTTS_CHECKPOINT}")
        else:
            print(" > Error: The specified custom model is not a valid .pth file path.")

    num_workers = 8
    if language == "ja":
        num_workers = 0
    # init args and config
    model_args = GPTArgs(
        max_conditioning_length=132300,  # 6 secs
        min_conditioning_length=66150,  # 3 secs
        debug_loading_failures=False,
        max_wav_length=max_audio_length,  # ~11.6 seconds
        max_text_length=200,
        mel_norm_file=MEL_NORM_FILE,
        dvae_checkpoint=DVAE_CHECKPOINT,
        xtts_checkpoint=XTTS_CHECKPOINT,  # checkpoint path of the model that you want to fine-tune
        tokenizer_file=TOKENIZER_FILE,
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )
    # define audio config
    audio_config = XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000)
    # training parameters config
    config = GPTTrainerConfig(
        epochs=num_epochs,
        output_path=OUT_PATH,
        model_args=model_args,
        run_name=RUN_NAME,
        project_name=PROJECT_NAME,
        run_description="""
            GPT XTTS training
            """,
        dashboard_logger=DASHBOARD_LOGGER,
        logger_uri=LOGGER_URI,
        audio=audio_config,
        batch_size=BATCH_SIZE,
        batch_group_size=48,
        eval_batch_size=BATCH_SIZE,
        num_loader_workers=num_workers,
        eval_split_max_size=256,
        run_eval_steps=100,
        print_step=50,
        plot_step=100,
        log_model_step=100,
        save_step=1500,
        save_n_checkpoints=1,
        save_checkpoints=True,
        # use_noise_augment = True,
        # shuffle=True,
        # drop_last=True,
        target_loss="loss", ## comentado
        print_eval=False,
        grad_clip=1.0,
        # Optimizer values like tortoise, pytorch implementation with modifications to not apply WD to non-weight parameters.
        optimizer="AdamW",
        cudnn_benchmark=True,
        optimizer_wd_only_on_weights=OPTIMIZER_WD_ONLY_ON_WEIGHTS,
        optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-3},
        lr=1e-05,  # learning rate 5e-06
         lr_scheduler="MultiStepLR",
        # it was adjusted accordly for the new step scheme
        lr_scheduler_params = {
            "milestones": [1200, 1900, 2600],
        #    "milestones": [0.4 * total_steps, 0.7 * total_steps, 0.9 * total_steps],
            "gamma": 0.5,
            "last_epoch": -1
        },
        test_sentences=[
        {
            "text": "De manhã, fui ao trabalho, minha mãe caminhava devagar, com a mão molhada, olhando o trovão com olhos estranhos. Parecia um sonho, ninguém falava, só o barulho do liquidificador.",
            "language": language,
            "speaker_wav": "E:/REPOS/xtts-finetune-webui/finetune_models/ready/reference0.wav"
        },
          {
            "text": "Ao trazer esse método para o Brasil, ele foi aconselhado por um amigo empresário de que se ensinasse as pessoas a falar inglês rápido, ele perderia muito dinheiro. Então era melhor esse curso.",
            "language": language,
            "speaker_wav": "E:/REPOS/xtts-finetune-webui/finetune_models/ready/reference0.wav"
        },
              {
            "text": "Naquela manhã, molhada de trovões, caminhava com um guarda-chuva pequeno e desastroso sem controle, o típico investimento que mãe diz pra não fazer. Molhou tudo. Enquanto olhava pro céu, pensei no controle que nunca tive. A vida inverta planos.",
            "language": language,
            "speaker_wav": "E:/REPOS/xtts-finetune-webui/finetune_models/ready/reference0.wav"
        }
    ],
    )

    # init the model from config
    model = GPTTrainer.init_from_config(config)

    dropout_aplicado = 0
    for module in model.modules():
        if isinstance(module, torch.nn.Dropout):
            module.p = dropout_rate
            dropout_aplicado += 1

    print(f"[✓] Dropout personalizado aplicado: {dropout_aplicado} camadas com p = {dropout_rate}")


    # load training samples
    train_samples, eval_samples = load_tts_samples(
        DATASETS_CONFIG_LIST,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # DEBUG MODE: Reduzir para só os 2 primeiros samples
    # train_samples = train_samples[:2]
    # eval_samples = eval_samples[:2]

    # Filtra apenas os samples cujo caminho do áudio contém "IA-"
    # eval_samples = [s for s in eval_samples if "ele" in s["audio_file"]]
    # train_samples = [s for s in train_samples if "ele" in s["audio_file"]]
    print(f"📃 Train samples: {len(train_samples)}")
    print(f"📃 Eval samples: {len(eval_samples)}")
    
    print("\n\n======== Params ========\n")

    # print every parameter
    for key, value in config.items():
        print(f"{key}: {value}")

    print("\n=======================\n\n")

    # init the trainer and 🚀
    trainer = Trainer(
        TrainerArgs(
            restore_path=None,  # xtts checkpoint is restored via xtts_checkpoint key so no need of restore it using Trainer restore_path parameter
            skip_train_epoch=False,
            start_with_eval=START_WITH_EVAL,
            grad_accum_steps=GRAD_ACUMM_STEPS,
        ),
        config,
        output_path=OUT_PATH,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()
    #depois:
    # for i in range(config.epochs):
    #     trainer.fit_epoch()
        
    #     # Gere amostra ao final de cada época
    #     generate_sample(
    #         model, 
    #         config, 
    #         text="Essa é uma amostra automática", 
    #         ref_audio=speaker_ref, 
    #         lang=language, 
    #         step=i + 1
    #     )



    # get the longest text audio file to use as speaker reference
    samples_len = [len(item["text"].split(" ")) for item in train_samples]
    longest_text_idx =  samples_len.index(max(samples_len))
    speaker_ref = train_samples[longest_text_idx]["audio_file"]

    trainer_out_path = trainer.output_path
    
    # close file handlers and remove them from the logger
    for handler in logging.getLogger('trainer').handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logging.getLogger('trainer').removeHandler(handler)
    
    # now you should be able to delete the log file
    log_file = os.path.join(trainer.output_path, f"trainer_{trainer.args.rank}_log.txt")
    os.remove(log_file)

    # deallocate VRAM and RAM
    del model, trainer, train_samples, eval_samples
    gc.collect()

    return XTTS_SPEAKER_FILE,XTTS_CONFIG_FILE, XTTS_CHECKPOINT, TOKENIZER_FILE, trainer_out_path, speaker_ref
