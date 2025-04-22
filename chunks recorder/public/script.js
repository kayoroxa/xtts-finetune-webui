let phrases = [];
let currentIndex = 0;
let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

const phraseDisplay = document.getElementById("phraseDisplay");
const referenceAudio = document.getElementById("referenceAudio");
const recordedAudio = document.getElementById("recordedAudio");

// Carrega o arquivo JSON com as frases
fetch('/phrases.json')
  .then(response => response.json())
  .then(data => {
    phrases = data.fragments;
    displayCurrentPhrase();
  });

// Exibe a frase atual na tela
function displayCurrentPhrase() {
  if (phrases.length > 0) {
    phraseDisplay.textContent = phrases[currentIndex].lines[0];
  }
}

// Toca o áudio de referência (localizado na pasta chunks com o mesmo ID)
function playReference() {
  const refId = phrases[currentIndex].id;
  referenceAudio.src = `chunks/${refId}.wav`;
  referenceAudio.style.display = "block";
  referenceAudio.play();
}

// Configura a gravação de áudio usando MediaRecorder
function initRecorder() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        // Cria blob a partir dos pedaços gravados
        const blob = new Blob(recordedChunks, { type: 'audio/wav' });
        recordedAudio.src = URL.createObjectURL(blob);
        recordedAudio.style.display = "block";
        recordedChunks = [];
        uploadAudio(blob);
      };
    })
    .catch(err => console.error("Erro ao acessar microfone:", err));
}

// Envia o áudio gravado para o servidor via POST
function uploadAudio(blob) {
  const formData = new FormData();
  formData.append('audio', blob, 'temp.wav');
  formData.append('phrase', phrases[currentIndex].lines[0]);

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      console.log(data.message, data.filename);
    })
    .catch(err => console.error("Erro ao enviar áudio:", err));
}

// Monitoramento de teclas para os atalhos
document.addEventListener('keydown', (e) => {
  // "r": Toca referência
  if (e.key === 'r' || e.key === 'R') {
    playReference();
  }
  // "Ctrl + Espaço": Inicia gravação
  if (e.code === 'Space' && e.ctrlKey) {
    if (!isRecording) {
      isRecording = true;
      if (!mediaRecorder) initRecorder();
      else mediaRecorder.start();
      console.log("Gravação iniciada...");
    }
  }
  // "Espaço" (sem ctrl): Para gravação / reproduz gravação se já tiver gravado
  if (e.code === 'Space' && !e.ctrlKey) {
    if (isRecording && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      isRecording = false;
      console.log("Gravação finalizada.");
    } else if (recordedAudio.src) {
      recordedAudio.play();
    }
  }
  // "d": Próxima frase
  if (e.key === 'd' || e.key === 'D') {
    if (currentIndex < phrases.length - 1) {
      currentIndex++;
      displayCurrentPhrase();
    }
  }
  // "a": Frase anterior
  if (e.key === 'a' || e.key === 'A') {
    if (currentIndex > 0) {
      currentIndex--;
      displayCurrentPhrase();
    }
  }
});

// Inicializa o MediaRecorder assim que a página carregar
window.addEventListener('load', initRecorder);
