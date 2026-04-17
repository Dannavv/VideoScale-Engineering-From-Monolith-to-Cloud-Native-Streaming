const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3001; // Project 2 on different port

// Allow CORS for streaming segments
app.use(cors());

// Serve the HLS output segments and playlists from the 'output' directory
app.use('/stream', express.static(path.join(__dirname, 'output')));

// Serve the frontend
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {
    console.log(`🎬 HLS Player running at http://localhost:${PORT}`);
    console.log(`📡 HLS Stream source: http://localhost:${PORT}/stream/master.m3u8`);
});
