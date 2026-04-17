const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.get('/video', (req, res) => {
    // 1. Get the range from headers
    const range = req.headers.range;
    if (!range) {
        res.status(400).send("Requires Range header");
        return;
    }

    // 2. Path to the video file (centralized)
    const videoPath = path.join(__dirname, '../../samples/sample1.mp4');

    // Check if file exists
    if (!fs.existsSync(videoPath)) {
        res.status(404).send("Video file not found. Please place 'sample.mp4' in the videos folder.");
        return;
    }

    const videoSize = fs.statSync(videoPath).size;

    // 3. Parse Range
    // Example: "bytes=32324-"
    const CHUNK_SIZE = 10 ** 6; // 1MB
    const start = Number(range.replace(/\D/g, ""));
    const end = Math.min(start + CHUNK_SIZE, videoSize - 1);

    // 4. Create headers
    const contentLength = end - start + 1;
    const headers = {
        "Content-Range": `bytes ${start}-${end}/${videoSize}`,
        "Accept-Ranges": "bytes",
        "Content-Length": contentLength,
        "Content-Type": "video/mp4",
    };

    // 5. HTTP Status 206 for Partial Content
    res.writeHead(206, headers);

    // 6. Create video read stream for this particular chunk
    const videoStream = fs.createReadStream(videoPath, { start, end });

    // 7. Pipe the read stream to the response
    videoStream.pipe(res);
});

app.listen(PORT, () => {
    console.log(`🚀 Video Streaming Server running at http://localhost:${PORT}`);
});
