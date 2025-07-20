document.addEventListener('DOMContentLoaded', function() {
    // --- Global Chatbot Elements (already defined) ---
     // --- Global Chatbot Elements ---
    const fabChatButton = document.getElementById('fab-chat-button');
    const floatingChatbotWindow = document.getElementById('floating-chatbot-window');
    const closeChatbotButton = document.getElementById('close-chatbot-button');
    // Ensure these elements are now selected from within the floating window
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMicButton = document.getElementById('chat-mic-button');
    const audioPlayer = document.getElementById('audio-player'); // Still global



// ... (chatbot functions like addMessageToChat, initializeChatbotWelcome, sendChatMessage) ...

    // --- Chatbot Widget Toggle Events ---
    if (fabChatButton && floatingChatbotWindow && closeChatbotButton) {
        fabChatButton.addEventListener('click', () => {
            floatingChatbotWindow.classList.add('active'); // Show
            initializeChatbotWelcome(); // Add welcome message when opening
            if (chatInput) { // Ensure chatInput exists before focusing
                chatInput.focus(); // Focus on input when opened
            }
        });

        closeChatbotButton.addEventListener('click', () => {
            floatingChatbotWindow.classList.remove('active'); // Hide
        });
    }

    // --- Event Listeners for Chatbot Input (now inside the floating window) ---
    if (sendButton && chatInput) {
        sendButton.addEventListener('click', () => {
            sendChatMessage(chatInput.value);
        });

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage(chatInput.value);
            }
        });
    }

    // Microphone functionality
    if (chatMicButton) { // Check if the mic button element exists
        chatMicButton.addEventListener('click', async () => {
            // ... (rest of mic button logic) ...
        });
    }

    let recognition;
    let isRecording = false;

    // --- Other Global Elements (Existing) ---
    const languageSwitcher = document.getElementById('language-switcher');
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarLinks = document.getElementById('navbar-links');

    // --- NEW: Weather Page Elements ---
    const weatherInput = document.getElementById('weather-city-input');
    const getWeatherButton = document.getElementById('get-weather-button');
    const weatherResultDiv = document.getElementById('weather-result');

    // --- NEW: Mandi Rates Page Elements ---
    const mandiStateSelect = document.getElementById('mandi-state-select');
    const mandiDistrictSelect = document.getElementById('mandi-district-select');
    const mandiCropSelect = document.getElementById('mandi-crop-select');
    const getMandiRatesButton = document.getElementById('get-mandi-rates-button');
    const mandiRatesResultDiv = document.getElementById('mandi-rates-result');

    // --- NEW: Schemes Page Elements ---
    const schemeCategorySelect = document.getElementById('scheme-category-select');
    const schemeStateSelect = document.getElementById('scheme-state-select');
    const getSchemesButton = document.getElementById('get-schemes-button');
    const schemesResultDiv = document.getElementById('schemes-result');

    // Crop Prediction Elements (from previous interactions, included for completeness)
    const cropImageInput = document.getElementById('crop-image-upload');
    const uploadCropButton = document.getElementById('upload-crop-button');
    const cropPredictionResultDiv = document.getElementById('crop-prediction-result');
    const uploadedImagePreview = document.getElementById('uploaded-image-preview');


    // --- Chatbot Functions (unchanged from previous response) ---
    function addMessageToChat(message, isUser = false, audioUrl = null) {
        if (!chatbotMessages) {
            console.error("Chatbot messages container not found!");
            return;
        }
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageElement.innerHTML = `<p>${message}</p>`;

        if (audioUrl) {
            const audioIcon = document.createElement('i');
            audioIcon.classList.add('fas', 'fa-volume-up', 'play-audio-icon');
            audioIcon.dataset.audioUrl = audioUrl;
            messageElement.appendChild(audioIcon);

            audioIcon.addEventListener('click', () => {
                if (audioPlayer) {
                    audioPlayer.src = audioUrl;
                    audioPlayer.play();
                }
            });
        }
        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function initializeChatbotWelcome() {
        if (chatbotMessages && chatbotMessages.children.length === 0) {
            if (window.userAuthenticated) {
                addMessageToChat(
                    "Hello! I am Kisaan Saathi, your AI assistant. How can I help you with your farming queries today?",
                    false
                );
            } else {
                addMessageToChat(
                    window.appMessages.loginRequiredChatbot,
                    false
                );
            }
        }
    }

    async function sendChatMessage(message) {
        if (message.trim() === '') return;
        if (!window.userAuthenticated) {
            addMessageToChat(window.appMessages.loginRequiredChatbot, false);
            chatInput.value = '';
            return;
        }
        addMessageToChat(message, true);
        chatInput.value = '';
        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, response_type: 'text' }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({error: `HTTP error! Status: ${response.status}`}));
                console.error('Server error:', errorData.error);
                addMessageToChat(`${window.appMessages.chatbotError}: ${errorData.error}`, false);
                return;
            }
            const data = await response.json();
            addMessageToChat(data.response, false, data.audio_url);
        } catch (error) {
            console.error('Error fetching chat response:', error);
            addMessageToChat(`${window.appMessages.chatbotError}: ${error.message}`, false);
        }
    }


    // --- Chatbot Widget Toggle Events (unchanged) ---
    if (fabChatButton && floatingChatbotWindow && closeChatbotButton) {
        fabChatButton.addEventListener('click', () => {
            floatingChatbotWindow.classList.add('active');
            initializeChatbotWelcome();
            if (chatInput) {
                chatInput.focus();
            }
        });

        closeChatbotButton.addEventListener('click', () => {
            floatingChatbotWindow.classList.remove('active');
        });
    }

    // --- Event Listeners for Chatbot Input (unchanged) ---
    if (sendButton && chatInput) {
        sendButton.addEventListener('click', () => {
            sendChatMessage(chatInput.value);
        });
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage(chatInput.value);
            }
        });
    }

    // Microphone functionality (unchanged)
    if (chatMicButton) {
        chatMicButton.addEventListener('click', async () => {
            if (!window.userAuthenticated) {
                addMessageToChat(window.appMessages.loginRequiredChatbot, false);
                return;
            }
            if (!('webkitSpeechRecognition' in window)) {
                alert(window.appMessages.speechRecognitionNotSupported);
                return;
            }
            if (!isRecording) {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = window.currentAppLang; // e.g., 'en', 'hi', 'bhojpuri' (ensure valid BCP 47)

                recognition.onstart = () => {
                    isRecording = true;
                    chatMicButton.classList.add('recording');
                    chatMicButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                    chatMicButton.title = window.appMessages.micOff;
                };
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    sendChatMessage(transcript);
                };
                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    addMessageToChat(`${window.appMessages.speechErrorGeneric}: ${event.error}`, false);
                    isRecording = false;
                    chatMicButton.classList.remove('recording');
                    chatMicButton.innerHTML = '<i class="fas fa-microphone"></i>';
                    chatMicButton.title = window.appMessages.micOn;
                };
                recognition.onend = () => {
                    isRecording = false;
                    chatMicButton.classList.remove('recording');
                    chatMicButton.innerHTML = '<i class="fas fa-microphone"></i>';
                    chatMicButton.title = window.appMessages.micOn;
                };
                recognition.start();
            } else {
                recognition.stop();
            }
        });
    }

    // --- Other Existing Event Listeners (unchanged) ---

    // Navbar Toggle for Mobile
    if (navbarToggle && navbarLinks) {
        navbarToggle.addEventListener('click', function() {
            navbarLinks.classList.toggle('active');
        });
    }

    // Language Switcher
    if (languageSwitcher) {
        languageSwitcher.addEventListener('change', function() {
            const selectedLang = this.value;
            window.location.href = `?lang=${selectedLang}`;
        });
    }


    // --- NEW: Weather Fetching Logic ---
    if (getWeatherButton && weatherInput && weatherResultDiv) {
        getWeatherButton.addEventListener('click', async () => {
            const city = weatherInput.value.trim();
            if (!city) {
                weatherResultDiv.innerHTML = `<p class="error-message">${window.appMessages.weather_no_city}</p>`;
                return;
            }

            weatherResultDiv.innerHTML = `<p>${window.appMessages.fetching_weather.replace('{city}', city)}</p>`; // Assuming fetching_weather message exists

            try {
                const response = await fetch(`/get_weather?city=${encodeURIComponent(city)}`);
                const data = await response.json();

                if (data.success) {
                    weatherResultDiv.innerHTML = `
                        <h3>${window.appMessages.weather_in} ${data.city}</h3>
                        <p>${window.appMessages.temperature}: ${data.temperature}°C</p>
                        <p>${window.appMessages.description}: ${data.description}</p>
                        <p>${window.appMessages.humidity}: ${data.humidity}%</p>
                        <p>${window.appMessages.wind_speed}: ${data.wind_speed} m/s</p>
                    `;
                } else {
                    weatherResultDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
                }
            } catch (error) {
                console.error('Error fetching weather:', error);
                weatherResultDiv.innerHTML = `<p class="error-message">${window.appMessages.weather_general_error}</p>`;
            }
        });
    }

    // --- NEW: Mandi Rates Logic ---
    if (getMandiRatesButton && mandiStateSelect && mandiDistrictSelect && mandiCropSelect && mandiRatesResultDiv) {

        const mandiData = {
            'Uttar Pradesh': ['Varanasi', 'Firozabad'],
            'Bihar': ['Patna']
        };

        // Populate districts based on selected state
        mandiStateSelect.addEventListener('change', () => {
            const selectedState = mandiStateSelect.value;
            mandiDistrictSelect.innerHTML = `<option value="">-- ${window.appMessages.select_district} --</option>`;
            if (selectedState && mandiData[selectedState]) {
                mandiData[selectedState].forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    mandiDistrictSelect.appendChild(option);
                });
            }
        });

        getMandiRatesButton.addEventListener('click', async () => {
            const state = mandiStateSelect.value;
            const district = mandiDistrictSelect.value;
            const crop = mandiCropSelect.value;

            if (!state || !district) {
                mandiRatesResultDiv.innerHTML = `<p class="error-message">${window.appMessages.select_state_district_prompt}</p>`; // Need a new message
                return;
            }

            mandiRatesResultDiv.innerHTML = `<p>${window.appMessages.fetching_mandi_rates}</p>`; // Need a new message

            try {
                let url = `/get_mandi_rates?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`;
                if (crop) {
                    url += `&crop=${encodeURIComponent(crop)}`;
                }

                const response = await fetch(url);
                const data = await response.json();

                if (data.success) {
                    let html = `<h3>${window.appMessages.mandi_rates_for} ${data.district}, ${data.state}</h3>`;
                    if (data.crop && data.crop !== 'all crops') { // If a specific crop was requested and found
                        html += `
                            <div class="mandi-item">
                                <h4>${data.crop}</h4>
                                <p>${window.appMessages.min_price}: ${data.rates.min} / ${data.rates.unit}</p>
                                <p>${window.appMessages.max_price}: ${data.rates.max} / ${data.rates.unit}</p>
                                <p>${window.appMessages.avg_price}: ${data.rates.avg} / ${data.rates.unit}</p>
                            </div>
                        `;
                    } else if (data.rates && typeof data.rates === 'object') { // If all crops for district were returned
                        for (const c in data.rates) {
                            const rate = data.rates[c];
                            html += `
                                <div class="mandi-item">
                                    <h4>${c}</h4>
                                    <p>${window.appMessages.min_price}: ${rate.min} / ${rate.unit}</p>
                                    <p>${window.appMessages.max_price}: ${rate.max} / ${rate.unit}</p>
                                    <p>${window.appMessages.avg_price}: ${rate.avg} / ${rate.unit}</p>
                                </div>
                            `;
                        }
                    } else {
                         html += `<p>${data.message || window.appMessages.no_specific_rates}</p>`; // Generic message if rates structure unexpected
                    }
                    mandiRatesResultDiv.innerHTML = html;
                } else {
                    mandiRatesResultDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
                }
            } catch (error) {
                console.error('Error fetching mandi rates:', error);
                mandiRatesResultDiv.innerHTML = `<p class="error-message">${window.appMessages.mandi_general_error}</p>`;
            }
        });
    }

    // --- NEW: Schemes Logic ---
    if (getSchemesButton && schemeCategorySelect && schemeStateSelect && schemesResultDiv) {
        getSchemesButton.addEventListener('click', async () => {
            const category = schemeCategorySelect.value;
            const state = schemeStateSelect.value;

            schemesResultDiv.innerHTML = `<p>${window.appMessages.fetching_schemes}</p>`; // Need a new message

            try {
                const response = await fetch(`/get_schemes_data?category=${encodeURIComponent(category)}&state=${encodeURIComponent(state)}`);
                const data = await response.json();

                if (data.success) {
                    let html = `<h3>${window.appMessages.schemes_found_title} (${data.schemes.length})</h3>`;
                    if (data.schemes.length > 0) {
                        data.schemes.forEach(scheme => {
                            html += `
                                <div class="scheme-item">
                                    <h4>${scheme.name}</h4>
                                    <p><strong>${window.appMessages.category}:</strong> ${scheme.category.charAt(0).toUpperCase() + scheme.category.slice(1)}</p>
                                    <p><strong>${window.appMessages.description}:</strong> ${scheme.description}</p>
                                    <p><strong>${window.appMessages.eligibility}:</strong> ${scheme.eligibility}</p>
                                </div>
                            `;
                        });
                    } else {
                        html += `<p>${data.message}</p>`;
                    }
                    schemesResultDiv.innerHTML = html;
                } else {
                    schemesResultDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
                }
            } catch (error) {
                console.error('Error fetching schemes:', error);
                schemesResultDiv.innerHTML = `<p class="error-message">${window.appMessages.schemes_general_error}</p>`;
            }
        });
    }

    // Crop Prediction Logic (from previous interactions, included for completeness)
    if (uploadCropButton && cropImageInput && cropPredictionResultDiv) {
        uploadCropButton.addEventListener('click', async () => {
            if (cropImageInput.files.length === 0) {
                cropPredictionResultDiv.innerHTML = `<p class="error-message">Please select a file first.</p>`;
                return;
            }

            const file = cropImageInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            cropPredictionResultDiv.innerHTML = `<p>Uploading and predicting...</p>`;
            if (uploadedImagePreview) {
                 uploadedImagePreview.innerHTML = '';
            }

            try {
                const response = await fetch('/upload_crop_image', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    cropPredictionResultDiv.innerHTML = `
                        <h3>Prediction Result:</h3>
                        <p>${data.prediction}</p>
                    `;
                    if (data.image_url && uploadedImagePreview) {
                        uploadedImagePreview.innerHTML = `<img src="${data.image_url}" alt="Uploaded Crop Image" style="max-width: 100%; height: auto; margin-top: 20px;">`;
                    }
                } else {
                    cropPredictionResultDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
                }
            } catch (error) {
                console.error('Error during crop prediction:', error);
                cropPredictionResultDiv.innerHTML = `<p class="error-message">An error occurred during prediction. Please try again.</p>`;
            }
        });
    }
});
