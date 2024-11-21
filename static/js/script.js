let canvas = document.getElementById('pixelCanvas');
let ctx = canvas.getContext('2d');
let pixelSize = 10;
let currentColor = '#000000'; // Default color: black

// Function to draw a pixel
function drawPixel(x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * pixelSize, y * pixelSize, pixelSize, pixelSize);
}

// Event listener to draw on the canvas
canvas.addEventListener("click", function(e) {
    let x = Math.floor(e.offsetX / pixelSize);
    let y = Math.floor(e.offsetY / pixelSize);
    drawPixel(x, y, currentColor);
});

// Set color for drawing
function setColor(color) {
    currentColor = color;
}

// Clear the canvas
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// Save the art (send data to Flask)
function saveArt() {
    let title = prompt("Enter a title for your art:");
    let description = prompt("Enter a description for your art:");

    // Convert canvas to image data (PNG)
    let imageData = canvas.toDataURL('image/png');  // Converts canvas to base64 PNG data

    // Send the data to Flask (POST request)
    fetch('/save_art', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `title=${title}&description=${description}&image_data=${imageData}`,
    }).then(response => {
        if (response.ok) {
            alert("Art saved!");
        } else {
            alert("Failed to save art.");
        }
    });
}
