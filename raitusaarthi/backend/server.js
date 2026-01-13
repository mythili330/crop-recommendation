import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import OpenAI from 'openai';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Route to handle AI requests
app.post('/api/chat', async (req, res) => {
  try {
    const { message, language } = req.body;

    const prompt = `
    You are RaituSaarthi, a friendly AI farming assistant.
    Answer this farmer's question in ${language}:
    "${message}"
    Give useful advice about crops, soil, weather, or farming techniques.
    `;

    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 250
    });

    const aiText = response.choices[0].message.content.trim();
    res.json({ reply: aiText });
  } catch (error) {
    console.error(error);
    res.status(500).json({ reply: "Sorry, something went wrong." });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(5001, () => console.log("Server running on port 5001"));
