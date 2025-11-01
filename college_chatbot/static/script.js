// This is the URL of your Django API.
// It's correct because our page is served from Django.
const API_URL = '/api/ask/';

// Get elements from the DOM
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatSubmit = document.getElementById('chat-submit');

// --- ADDED: Get the new mic button ---
const micBtn = document.getElementById('mic-btn');
// ------------------------------------

// Listen for form submission
chatForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Stop page from reloading
    handleFormSubmit();
});

// --- ADDED: Extracted form submission to a function ---
function handleFormSubmit() {
    const question = chatInput.value.trim();
    if (!question) return;

    // 1. Display user's question (no formatting)
    addMessage(question, 'user');
    
    // 2. Clear the input and disable the form
    chatInput.value = '';
    chatInput.disabled = true;
    chatSubmit.disabled = true;
    if (micBtn) micBtn.disabled = true; // FIX: Check if micBtn exists
    
    // 3. Show a "thinking" message
    const thinkingMsg = addMessage('Thinking...', 'bot', 'thinking');

    // 4. Send the question to the backend
    fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Django requires a CSRF token. We can get it from the page,
            // but for this simple setup, our view uses @csrf_exempt.
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => {
        if (!response.ok) {
            // Handle server errors (like 500)
            return response.json().then(err => {
                throw new Error(err.error || 'Server error');
            });
        }
        return response.json();
    })
    .then(data => {
        // 5. Remove "thinking" message
        thinkingMsg.remove();
        
        // 6. Display the bot's real answer
        // This correctly looks for "answer" which matches your views.py
        if (data.answer) {
            addMessage(data.answer, 'bot', data.source);
        } else {
            addMessage('Sorry, I encountered an error.', 'bot', 'Error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        thinkingMsg.remove();
        addMessage(`Error: ${error.message}`, 'bot', 'Error');
    })
    .finally(() => {
        // 7. Re-enable the form
        chatInput.disabled = false;
        chatSubmit.disabled = false;
        if (micBtn) micBtn.disabled = false; // FIX: Check if micBtn exists
        chatInput.focus();
    });
}
// ----------------------------------------------------


// Helper function to add a message to the chat window
function addMessage(text, sender, source = '') {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'user-msg' : 'bot-msg');

    if (sender === 'user') {
        // User text should be plain text
        msgDiv.textContent = text;
    } else {
        // --- THIS IS THE FORMATTING FIX ---
        // Bot text is now run through the 'marked' library
        // to convert Markdown (like * bullets) into HTML
        
        // This is a "thinking..." message
        if (source === 'thinking') {
            msgDiv.id = 'thinking-msg';
            msgDiv.innerHTML = '<p>Thinking...</p>';
        } else {
            // This is a real bot answer
            // We use marked.parse() to convert text to HTML
            const formattedText = marked.parse(text);
            msgDiv.innerHTML = formattedText;
        }
        
        // Add the source
        if (source && source !== 'thinking') {
            const sourceDiv = document.createElement('div');
            sourceDiv.classList.add('source');
            sourceDiv.textContent = `Source: ${source}`;
            msgDiv.appendChild(sourceDiv);
        }
    }
    
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
    return msgDiv; // Return the message element
}


// --- ADDED: WEB SPEECH API (VOICE TYPING) LOGIC ---

// Check if the browser supports the SpeechRecognition API
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition && micBtn) { // FIX: Check if micBtn exists
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop after one phrase
    recognition.lang = 'en-US';       // Set language
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    // Event listener for the mic button
    micBtn.addEventListener('click', () => {
        try {
            recognition.start();
            micBtn.classList.add('recording');
            micBtn.textContent = '...';
        } catch(e) {
            console.error("Speech recognition already active", e);
        }
    });

    // When speech is recognized
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        
        // Optional: Automatically send the message after speaking
        // handleFormSubmit(); 
    };

    // When recognition ends
    recognition.onend = () => {
        micBtn.classList.remove('recording');
        micBtn.textContent = '🎤';
    };

    // Handle errors
    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        micBtn.classList.remove('recording');
        micBtn.textContent = '🎤';
        addMessage(`Speech Error: ${event.error}`, 'bot', 'Error');
    };  

} else {
    // Browser doesn't support speech recognition
    console.warn("Browser doesn't support SpeechRecognition or mic-btn is missing.");
    if (micBtn) micBtn.style.display = 'none'; // Hide the mic button if it exists but API is unsupported
}
// ----------------------------------------------------
// FIX: REMOVED THE EXTRA '}' THAT WAS HERE

