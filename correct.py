import pandas as pd


def verificar_csv(path):
    colunas_esperadas = ['audio_file', 'text', 'speaker_name', 'language']

    try:
        df = pd.read_csv(path, sep="|")

        if list(df.columns) != colunas_esperadas:
            return False, "Colunas incorretas ou fora de ordem."

        if df.isnull().values.any():
            return False, "Há valores nulos no CSV."

        # Verifica se todos os valores são strings (linha por linha)
        for col in df.columns:
            if not df[col].map(lambda x: isinstance(x, str)).all():
                return False, f"A coluna '{col}' contém valores que não são strings."

        return True, "CSV está válido."

    except Exception as e:
        return False, f"Erro ao ler ou validar o CSV: {e}"



print(verificar_csv("finetune_models\dataset\metadata_train.csv"))
print(verificar_csv("finetune_models\dataset\metadata_eval.csv"))
