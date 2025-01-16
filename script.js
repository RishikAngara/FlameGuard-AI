function uploadImage() {
    const input = document.getElementById('imageInput');
    const resultText = document.getElementById('result');
    
    if (input.files.length === 0) {
        resultText.textContent = 'Please select an image.';
        return;
    }

    const formData = new FormData();
    formData.append('file', input.files[0]);

    fetch('/predict', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        resultText.textContent = 'Prediction: ' + data.prediction;
    })
    .catch(error => {
        console.error('Error:', error);
        resultText.textContent = 'Error occurred during prediction.';
    });
}
