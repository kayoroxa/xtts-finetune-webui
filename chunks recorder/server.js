const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

// Cria pastas se não existirem
const recordingsDir = path.join(__dirname, 'recordings');
if (!fs.existsSync(recordingsDir)) fs.mkdirSync(recordingsDir);

const metadataFile = path.join(__dirname, 'metadata.csv');
if (!fs.existsSync(metadataFile)) fs.writeFileSync(metadataFile, 'audio_file|text|speaker_name\n');

const app = express();
const PORT = 3000;

// Configurar multer para receber arquivos de áudio
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, recordingsDir);
  },
  filename: function (req, file, cb) {
    // Gera nome sequencial baseado na quantidade de arquivos já salvos
    const files = fs.readdirSync(recordingsDir);
    const nextNumber = 1560 + files.length;  // exemplo: começa a partir de 1560
    cb(null, `segment_${nextNumber}.wav`);
  }
});

const upload = multer({ storage: storage });

// Serve arquivos estáticos da pasta public
app.use(express.static('public'));

// Endpoint para receber o upload do áudio
app.post('/upload', upload.single('audio'), (req, res) => {
  // Dados enviados do cliente: frase atual
  const { phrase } = req.body;
  const filename = path.join('recordings', req.file.filename);
  const speaker = "caio"; // Nome fixo, pode ser parametrizado

  // Adiciona nova linha no metadata.csv
  const line = `${filename}|${phrase}|${speaker}\n`;
  fs.appendFileSync(metadataFile, line);

  res.json({ message: 'Upload realizado com sucesso!', filename });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
