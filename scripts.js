const notes = ['C', 'Csharp', 'D', 'Dsharp', 'E', 'F', 'Fsharp', 'G', 'Gsharp', 'A', 'Asharp', 'B', 'C2'];
let generatedTune = [];
let userInput = [];

document.addEventListener('DOMContentLoaded', () => {
    const keys = document.querySelectorAll('.key');
    const playButton = document.getElementById('play-button');
    const restartButton = document.getElementById('restart-button');
    const lengthInput = document.getElementById('length-value');

    // Create popup elements
    const popupOverlay = document.createElement('div');
    const popupBox = document.createElement('div');
    const closeBtn = document.createElement('span');

    popupOverlay.classList.add('popup-overlay');
    popupBox.classList.add('popup-box');
    closeBtn.classList.add('close-btn');
    closeBtn.innerHTML = '&times;';
    popupBox.appendChild(closeBtn);
    popupOverlay.appendChild(popupBox);
    document.body.appendChild(popupOverlay);

    keys.forEach(key => {
        key.addEventListener('click', () => {
            playSound(key);
            const note = key.getAttribute('data-note');
            userInput.push(note);
            if (userInput.length === generatedTune.length) {
                checkTune();
            }
        });
    });

    playButton.addEventListener('click', () => {
        const lengthOfSequence = parseInt(lengthInput.value);
        if (!isNaN(lengthOfSequence) && lengthOfSequence > 0) {
            generateTune(lengthOfSequence);
            userInput = [];
            playSequence(lengthOfSequence);
        } else {
            alert('Please enter a valid number for the length of the tune.');
        }
    });

    restartButton.addEventListener('click', () => {
        userInput = [];
        playSequence(generatedTune.length);
    });

    closeBtn.addEventListener('click', hidePopup);

    popupOverlay.addEventListener('click', (e) => {
        if (e.target === popupOverlay) {
            hidePopup();
        }
    });

    function playSound(key) {
        const note = key.getAttribute('data-note');
        const audio = new Audio(`sounds/${note}.mp3`);
        audio.play();
    }

    function playNote(note) {
        const audio = new Audio(`sounds/${note}.mp3`);
        audio.play();
    }

    function generateRandomNote() {
        const randomIndex = Math.floor(Math.random() * notes.length);
        return notes[randomIndex];
    }

    async function playSequence(length) {
        for (let i = 0; i < length; i++) {
            const note = generatedTune[i];
            playNote(note);
            const key = document.querySelector(`.key[data-note="${note}"]`);
            key.classList.add('active');
            await sleep(500);
            key.classList.remove('active');
            await sleep(500);
        }
    }

    function generateTune(length) {
        generatedTune = [];
        for (let i = 0; i < length; i++) {
            generatedTune.push(generateRandomNote());
        }
        console.log('Generated Tune:', generatedTune);
    }

    function showPopup(message) {
        popupBox.innerHTML = `${message} <span class="close-btn">&times;</span>`;
        const newCloseBtn = popupBox.querySelector('.close-btn');
        newCloseBtn.addEventListener('click', hidePopup);
        popupOverlay.classList.add('show');
    }

    function hidePopup() {
        popupOverlay.classList.remove('show');
    }

    function checkTune() {
        for (let i = 0; i < userInput.length; i++) {
            if (userInput[i] !== generatedTune[i]) {
                showPopup('Try Again!');
                userInput = [];
                return;
            }
        }
        showPopup('Good Job!');
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
});
