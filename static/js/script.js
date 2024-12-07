// Reference the canvas and context
const canvas = document.getElementById('pixelCanvas');
const ctx = canvas.getContext('2d');

// Set the initial canvas settings
const pixelSize = 16; // Size of each pixel
const rows = canvas.width / pixelSize; // Number of rows
const cols = canvas.height / pixelSize; // Number of columns

// Fill the canvas with a default color (optional)
ctx.fillStyle = "#ffffff"; // Default canvas background
ctx.fillRect(0, 0, canvas.width, canvas.height);

// Drawing state
let isDrawing = false;
let selectedColor = "#000000"; // Default color

// Event listeners for drawing
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    drawPixel(e); // Draw on initial click
});

canvas.addEventListener('mousemove', (e) => {
    if (isDrawing) {
        drawPixel(e);
    }
});

canvas.addEventListener('mouseup', () => {
    isDrawing = false;
});

canvas.addEventListener('mouseleave', () => {
    isDrawing = false; // Stop drawing if mouse leaves canvas
});

// Event listener for the color picker
document.getElementById('colorPicker').addEventListener('input', (e) => {
    selectedColor = e.target.value;
});

// Function to calculate and draw the pixel
function drawPixel(event) {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / pixelSize) * pixelSize;
    const y = Math.floor((event.clientY - rect.top) / pixelSize) * pixelSize;

    ctx.fillStyle = selectedColor;
    ctx.fillRect(x, y, pixelSize, pixelSize);
}

// Clear canvas function
function clearCanvas() {
    ctx.fillStyle = "#ffffff"; // Reset to default color
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// Save art function (converts canvas to base64)
function saveArt() {
    const imageData = canvas.toDataURL(); // Get base64 image data
    const title = prompt("Enter a title for your artwork:");
    const description = prompt("Enter a description:");

    if (!title || !description) {
        alert("Title and description are required.");
        return;
    }

    // Send data to the server
    fetch('/save_art', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            title,
            description,
            image_data: imageData,
        }),
    })
        .then((response) => {
            if (response.ok) {
                alert("Artwork saved!");
                window.location.href = '/gallery'; // Redirect to gallery
            } else {
                alert("Failed to save artwork.");
            }
        })
        .catch((error) => console.error('Error saving artwork:', error));
}
