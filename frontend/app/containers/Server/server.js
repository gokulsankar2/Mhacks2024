const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const port = 5000;

// Configure multer to save files to a specific path
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');  // Specify upload folder
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);  // Generate a unique filename
  }
});

const upload = multer({ storage });

// Create upload folder if it doesn't exist
const fs = require('fs');
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)){
    fs.mkdirSync(uploadDir);
}

// Endpoint to handle file upload
app.post('/upload', upload.single('video'), (req, res) => {
  res.send('File uploaded successfully');
});

app.listen(port, () => {
  console.log(`Server started on http://localhost:${port}`);
});