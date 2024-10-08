const express = require('express');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const port = 9999;

app.use(cors());
app.use(express.json());

// Set default charset for all responses
app.use((req, res, next) => {
  res.charset = 'utf-8';
  next();
});

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Serve index.html for the root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

function handlePythonProcess(req, res, endpoint) {
    const { url, language } = req.body;
    
    const pythonProcess = spawn('python', ['conjureReadme.py', endpoint, url, language]);
    
    let result = '';
    
    pythonProcess.stdout.on('data', (data) => {
        result += data.toString('utf-8');
    });
    
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });
    
    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).send('An error occurred while processing the README');
        }
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.send(result);
    });
}

app.post('/showReadme', (req, res) => {
    handlePythonProcess(req, res, '/showReadme');
});

app.post('/conjureReadme', (req, res) => {
    handlePythonProcess(req, res, '/conjureReadme');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});