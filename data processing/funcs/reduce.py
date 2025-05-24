import os
import subprocess

# Caminho da pasta atual (onde o script está)
dirname = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(dirname, "wavs")
output_folder = os.path.join(dirname, "flac_compact")

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".wav"):
        input_path = os.path.join(input_folder, filename)
        output_name = os.path.splitext(filename)[0] + ".flac"
        output_path = os.path.join(output_folder, output_name)

        print(f"Convertendo: {filename}")
        command = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ac", "1",
            "-ar", "24000",
            "-c:a", "flac",
            output_path
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("✅ Conversão concluída.")
