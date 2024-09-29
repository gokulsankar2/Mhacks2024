const fs = require('fs');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');

// Define paths
const filePath = __dirname;
const videoPath = path.join(filePath, 'capture', 'testvid.MOV');

// Function to extract frames from video
export function extractFrameFromVideo(videoFilePath, frames = null, captureRate = 1) {
    console.log(`Extracting ${videoFilePath} at 1 frame per second. This might take a bit...`);

    let output_file_prefix = path.basename(videoFilePath, path.extname(videoFilePath)).replace('.', '_');
    let frameCount = 0;
    let frameRate = 0; // We'll set this after getting video info
    let vidnum = 0;
    let addedFolder = false;

    if (!fs.existsSync(path.join(filePath, `content/vid${vidnum}`))) {
        fs.mkdirSync(path.join(filePath, `content/vid${vidnum}`), { recursive: true });
    }

    console.log(`Starting extraction of video: ${vidnum}`);

    ffmpeg.ffprobe(videoFilePath, (err, metadata) => {
        if (err) throw err;

        // Get frames per second
        frameRate = metadata.streams[0].avg_frame_rate.split('/').reduce((a, b) => a / b);
        console.log(frameRate);

        ffmpeg(videoFilePath)
            .on('end', () => {
                console.log(`Completed video frame extraction!\n\nExtracted: ${frameCount / captureRate} frames`);
            })
            .on('error', (err) => {
                console.error('Error in video processing:', err);
            })
            .on('start', (commandLine) => {
                console.log('Spawned Ffmpeg with command: ' + commandLine);
            })
            .on('filenames', (filenames) => {
                console.log('Screenshots taken are ' + filenames.join(', '));
            })
            .screenshots({
                count: frames || (metadata.format.duration * frameRate),
                folder: path.join(filePath, `content/vid${vidnum}`),
                filename: `${output_file_prefix}_frame%02i.jpg` 
            })
            .withOutputOptions([`-vf fps=${captureRate}`]);
    });
}

// Start the frame extraction
extractFrameFromVideo(videoPath, 120, 2);