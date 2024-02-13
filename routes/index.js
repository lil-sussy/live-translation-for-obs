import dotenv from 'dotenv';
dotenv.config();
import express from 'express';
import path from 'path';
import fetch from 'node-fetch';
const app = express();
const PORT = process.env.PORT || 3001;

// Middleware to parse JSON bodies
app.use(express.json());

// Middleware to serve static files from 'public' directory
app.use(express.static('public'));


const router = express.Router();

// Example usage of the path module
router.get('/', (req, res, next) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// app.get('/', (req, res) => {
//     res.sendFile(path.join(__dirname, 'public', 'translate.html'));
// });

// Endpoint to handle translation requests
app.post('/translate', async (req, res) => {
    const { text, source_lang, target_lang } = req.body;
    console.log('ok');
    var DEEPL_KEY = '83e31615-d5fa-1097-d2aa-d7e99a8559b7:fx'
    const response = await fetch('https://api-free.deepl.com/v2/translate', {
        method: 'POST',
        headers: {
            'Authorization': `DeepL-Auth-Key ${process.env.DEEPL_KEY}`,
            'DeepL-Auth-Key': DEEPL_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: {
            text: text,
            source_lang: source_lang,
            target_lang: target_lang
          }
    });
    console.log(response);
    const data = await response.json();
    console.log(data);
    res.json(response);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

export default app;