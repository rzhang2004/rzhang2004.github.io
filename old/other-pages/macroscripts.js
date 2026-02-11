document.addEventListener('DOMContentLoaded', function() {

    const allergensLink = document.getElementById('allergens');

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

    if (allergensLink) {
        allergensLink.addEventListener('click', function(event) {
            event.preventDefault();
            showPopup("Common allergens include: milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, and soybeans.");
        });
    }

    closeBtn.addEventListener('click', hidePopup);
});

function showPopup(message) {
    const popupBox = document.querySelector('.popup-box');
    popupBox.innerHTML = `${message} <span class="close-btn">&times;</span>`;
    const newCloseBtn = popupBox.querySelector('.close-btn');
    newCloseBtn.addEventListener('click', hidePopup);
    document.querySelector('.popup-overlay').classList.add('show');
}

function hidePopup() {
    document.querySelector('.popup-overlay').classList.remove('show');
}

function syncValue(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const input = document.getElementById(inputId);
    if (slider && input) {
        input.value = slider.value;
        calculateCalories();
    }
}

function calculateCalories() {
    const protein = parseFloat(document.getElementById('int1').value) || 0;
    const carbs = parseFloat(document.getElementById('int2').value) || 0;
    const fats = parseFloat(document.getElementById('int3').value) || 0;
    const totalCalories = protein * 4 + carbs * 4 + fats * 9;
    const caloriesInput = document.getElementById('int4');
    if (caloriesInput) {
        caloriesInput.value = !isNaN(totalCalories) ? totalCalories.toFixed(2) : 0;
    }
}
