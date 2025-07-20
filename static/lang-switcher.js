  const switcher = document.getElementById("languageSwitcher");
    const featuresList = document.getElementById("features-list").children;
    const missionText = document.getElementById("mission-text");
    const voiceTextHeading = document.getElementById("voice-text-heading");
    const voiceTextDesc = document.getElementById("voice-text-desc");

    function updateLanguage(lang) {
      missionText.innerText = missionText.dataset[lang] || missionText.dataset['en'];
      voiceTextHeading.innerText = voiceTextHeading.dataset[lang] || voiceTextHeading.dataset['en'];
      voiceTextDesc.innerText = voiceTextDesc.dataset[lang] || voiceTextDesc.dataset['en'];
      for (let li of featuresList) {
        li.innerText = li.dataset[lang] || li.dataset['en'];
      }
    }

    switcher.addEventListener("change", (e) => {
      updateLanguage(e.target.value);
    });

    // Default to English initially
    updateLanguage("en");

switcher.addEventListener("change", (e) => {
  updateLanguage(e.target.value);
});

// Default to English initially
updateLanguage("en");

