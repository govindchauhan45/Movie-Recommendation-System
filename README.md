🎬 AI Movie Recommendation System

An AI-powered movie recommendation system that suggests movies based on a user's current mood and preferred language.

The system uses Artificial Intelligence and movie APIs to provide personalized recommendations with detailed movie insights including ratings, plot summaries, posters, and streaming platforms.

📖 Project Overview

Choosing a movie to watch can sometimes be difficult due to the vast number of options available.

This AI system solves that problem by recommending movies based on a user's emotional state and language preference.

The system supports mood categories such as:

😊 Happy
😢 Sad
❤️ Romantic
🔥 Action
😂 Funny
😱 Thriller

By combining AI-generated recommendations with movie data APIs, the system provides smart and context-aware movie suggestions.

✨ Key Features
🎭 Mood-Based Recommendations

Users receive movie suggestions tailored to their current emotional state.

🤖 AI-Powered Recommendation Engine

Uses AI models to generate intelligent suggestions beyond simple keyword matching.

🎬 Movie Metadata Integration

Fetches rich movie details including:

Poster

IMDb Rating

Plot Summary

Genre

Actors

Release Year

using the OMDb API.

📺 Streaming Platform Detection

Shows where a movie is available to watch using the Watchmode API.

⚡ High-Performance Backend

Built with FastAPI for fast and scalable API performance.

🌐 Frontend Compatible API

The backend API can easily integrate with modern frameworks like:

React

Next.js

Mobile applications

Progressive Web Apps

🔐 Secure Configuration

Sensitive API keys are stored securely using environment variables (.env).

🛠 Tech Stack
Backend

Python

FastAPI

Pydantic

AI Integration

OpenAI

Microsoft Azure OpenAI Service

APIs

OMDb API – Movie information

Watchmode API – Streaming platform detection

Tools & Libraries

Uvicorn

Requests

Python-dotenv
###
📂 Project Structure
Movie-Recommendation-Using-AI
│
├── app.py                  # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not pushed to GitHub)
│
├── front/                  # Frontend application
│   ├── index.html
│   ├── app.js
│   ├── sw.js
│   └── manifest.json
│
└── README.md

⚙ Installation
1️⃣ Clone the Repository
git clone https://github.com/govindchauhan-s/Movie-Recommendation-Using-AI.git
cd Movie-Recommendation-Using-AI
2️⃣ Create Virtual Environment
python -m venv env

Activate it:

Windows

env\Scripts\activate

Mac / Linux

source env/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Setup Environment Variables

Create a .env file:

AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
WATCHMODE_API_KEY=your_key
OMDB_API_KEY=your_key
▶ Running the Application

Start the API server:

uvicorn app:app --reload

Server will start at:

http://localhost:8000

Interactive API docs:

http://localhost:8000/docs
🚦 API Endpoints
Root Endpoint
GET /

Returns API status.

Health Check
GET /health

Checks whether APIs are working properly.

Movie Recommendation
POST /recommend
Example Request
{
  "mood": "happy",
  "language": "english"
}
Example Response
{
  "success": true,
  "recommendations": [
    {
      "title": "Forrest Gump",
      "year": "1994",
      "rating": "8.8",
      "genre": "Drama"
    }
  ]
}
🌍 Deployment Options

You can deploy this project on cloud platforms such as:

Render

Railway

Vercel

Amazon Web Services

Docker

🤝 Contributing

Contributions are welcome.

Steps:

Fork the repository

Create a new feature branch

Commit your changes

Push the branch

Open a Pull Request

⭐ Support

If you find this project useful, please star the repository ⭐ on GitHub to support the project.

👨‍💻 Author

Govind Chauhan

GitHub
https://github.com/govindchauhan45
