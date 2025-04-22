const fs = require('fs');
const path = require('path');

// Configurações
const MIN_PALAVRAS = 3;
const MAX_PALAVRAS = 10;
const filter = false;

// Caminho do arquivo
const filePath = path.join(__dirname, 'text.txt');

// Lê o conteúdo do arquivo
let texto = fs.readFileSync(filePath, 'utf8');

// Remove quebras de linha
texto = texto.replace(/\n+/g, ' ');

// Divide em frases com base nos sinais de pontuação
let frasesBrutas = texto.split(/(?<=[.!?])\s+/);

// Processa as frases
let frasesProcessadas = [];

for (let frase of frasesBrutas) {
  const palavras = frase.trim().split(/\s+/);

  if (!filter) {
    // Se filter é false, adiciona a frase completa
    frasesProcessadas.push(frase.trim());
  } else {
    // Fragmenta a frase em blocos de até MAX_PALAVRAS e no mínimo MIN_PALAVRAS
    for (let i = 0;i < palavras.length;i += MAX_PALAVRAS) {
      const chunk = palavras.slice(i, i + MAX_PALAVRAS);
      if (chunk.length >= MIN_PALAVRAS) {
        frasesProcessadas.push(chunk.join(' '));
      }
    }
  }
}

// Junta as frases processadas com \n e sobrescreve o arquivo
fs.writeFileSync(filePath, frasesProcessadas.join('\n'), 'utf8');

console.log('Arquivo processado com sucesso.');
