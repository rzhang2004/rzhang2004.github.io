document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.toolbar-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            document.querySelector(`#${button.textContent.toLowerCase()}`).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
