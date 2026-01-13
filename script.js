const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const imageUpload = document.getElementById('imageUpload');
const analyzeBtn = document.getElementById('analyzeBtn');

function addMessage(text, sender='bot') {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', sender);
  msgDiv.textContent = text;
  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function detectLanguage(text) {
  if (/[అ-హ]/.test(text)) return 'te-IN';
  if (/[क-ह]/.test(text)) return 'hi-IN';
  return 'en-US';
}

function speak(text, lang='en-US') {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  speechSynthesis.speak(utterance);
}

async function getAIResponse(message) {
  try {
    const lang = detectLanguage(message);
    let language = 'English';
    if(lang === 'hi-IN') language = 'Hindi';
    else if(lang === 'te-IN') language = 'Telugu';

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message, language: language })
    });

    const data = await res.json();
    return data.reply;
  } catch (err) {
    console.error(err);
    return "Sorry, I couldn't get an answer right now.";
  }
}

async function sendMessage() {
  const message = userInput.value.trim();
  if(!message) return;
  addMessage(message, 'user');
  const aiResponse = await getAIResponse(message);
  addMessage(aiResponse, 'bot');
  speak(aiResponse, detectLanguage(message));
  userInput.value = '';
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });

voiceBtn.addEventListener('click', () => {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-IN';
  recognition.start();
  recognition.onresult = (event) => {
    const speech = event.results[0][0].transcript;
    userInput.value = speech;
    sendMessage();
  };
});

analyzeBtn.addEventListener('click', async () => {
  if(!imageUpload.files[0]) { alert("Please upload an image first!"); return; }
  const formData = new FormData();
  formData.append('image', imageUpload.files[0]);

  try {
    const res = await fetch('/api/analyze-image', { method: 'POST', body: formData });
    const data = await res.json();
    addMessage("Analysis: " + data.result, 'bot');
    speak(data.result, detectLanguage(data.result));
  } catch(err) {
    console.error(err);
    addMessage("Error analyzing image.", 'bot');
  }
});

addMessage("🌾 Namaste! I am RaituSaarthi. Ask me anything about farming in English, Hindi, or Telugu.", 'bot');
speak("Namaste! I am RaituSaarthi. Ask me anything about farming in English, Hindi, or Telugu.");
