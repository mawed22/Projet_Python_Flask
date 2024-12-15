// document.getElementById('date').value = new Date().toLocaleDateString("fr");
// const value = document.querySelector("#ratingvalue");
// const input = document.querySelector("#rating");
// value.textContent = input.value;
// input.addEventListener("input", (event) => {
//   value.textContent = event.target.value;
// });

document.getElementById('date').value = new Date().toLocaleDateString("fr");

const value = document.querySelector("#ratingvalue");
const input = document.querySelector("#rating");
value.textContent = input.value;
input.addEventListener("input", (event) => {
  value.textContent = event.target.value;
});

document.getElementById('feedback-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);

    fetch('/submit_feedback', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Votre retour a été enregistré avec succès !');
            this.reset();
        } else {
            alert('Erreur : ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de l\'envoi du formulaire.');
    });
});