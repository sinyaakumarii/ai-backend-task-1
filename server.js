const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
    res.status(200).json({
        success: true,
        message: "Hello this is my first assignment for FlyRank AI"
    });
});

app.get('/portfolio', (req, res) => {
    res.status(200).json({
        success: true,
        message: "Check my work here: [Your GitHub Link]"
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});