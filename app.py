from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import re
import time

# Load environment variables
load_dotenv()

app = FastAPI(title="Movie Mood Recommender API", version="1.0.0")

# CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.netlify.app",
        "https://*.vercel.app", 
        "http://localhost:3000",
        "http://localhost:5000",
        "*"  # Remove this in production and specify your frontend URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try Azure OpenAI setup
try:
    from openai import AzureOpenAI
    
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://selva-mcq499f7-eastus2.cognitiveservices.azure.com/")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2026-03-06-preview")
    
    if azure_api_key:
        client = AzureOpenAI(
            api_key=azure_api_key,
            api_version=azure_api_version,
            azure_endpoint=azure_endpoint
        )
        OPENAI_AVAILABLE = True
        print("✅ Azure OpenAI client configured")
    else:
        print("⚠️ Azure OpenAI API key not found")
        OPENAI_AVAILABLE = False
        
except Exception as e:
    print(f"⚠️ OpenAI setup failed: {e}")
    OPENAI_AVAILABLE = False

# API Keys
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "196872fc")
WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")

LANGUAGE_MAP = {
    "english": "English", "hindi": "Hindi", "tamil": "Tamil", "telugu": "Telugu",
    "french": "French", "german": "German", "korean": "Korean",
    "japanese": "Japanese", "spanish": "Spanish", "italian": "Italian", 
    "chinese": "Chinese", "all": "All Languages"
}

class MoodRequest(BaseModel):
    mood: str
    language: str

@app.get("/")
def read_root():
    """API root endpoint"""
    return {
        "message": "Movie Mood Recommender API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "recommend": "/recommend (POST)",
            "health": "/health (GET)",
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Movie Mood Recommender API is running",
        "openai_available": OPENAI_AVAILABLE,
        "watchmode_available": bool(WATCHMODE_API_KEY)
    }

@app.post("/recommend")
def recommend_movies(req: MoodRequest):
    """Main recommendation endpoint"""
    try:
        language = LANGUAGE_MAP.get(req.language.lower(), "English")
        
        # Strategy 1: Try OpenAI if available
        if OPENAI_AVAILABLE:
            try:
                titles = get_openai_recommendations(req.mood, language)
                if titles:
                    print(f"✅ OpenAI found {len(titles)} movies")
                else:
                    print("⚠️ OpenAI returned no results, using fallback")
                    titles = get_fallback_movies(req.mood, req.language.lower())
            except Exception as e:
                print(f"❌ OpenAI failed: {e}")
                titles = get_fallback_movies(req.mood, req.language.lower())
        else:
            print("⚠️ OpenAI not available, using fallback movies")
            titles = get_fallback_movies(req.mood, req.language.lower())

        # Get detailed information for each movie
        results = []
        for title in titles[:15]:  # Limit to 15 movies
            info = fetch_movie_info(title)
            if info:
                results.append(info)
            else:
                # Add basic info if OMDB fails
                results.append({
                    "title": title,
                    "year": "2020",
                    "poster": None,
                    "rating": "7.5",
                    "plot": f"An engaging {req.mood} movie worth watching.",
                    "platforms": ["Netflix", "Amazon Prime"]
                })

        if not results:
            raise HTTPException(status_code=404, detail="No movies found")

        return {
            "success": True,
            "recommendations": results,
            "total": len(results),
            "mood": req.mood,
            "language": language
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in recommend_movies: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def get_openai_recommendations(mood, language):
    """Get movie recommendations using OpenAI"""
    try:
        prompt = (
            f"Suggest 15 excellent movies based on the mood: '{mood}'\n\n"
            f"Language preference: {language}\n"
            f"Requirements:\n"
            f"- Only suggest real, well-known movies\n"
            f"- Include both classic and modern films\n"
            f"- For Hindi/Tamil include Indian movies\n"
            f"- For English include Hollywood movies\n\n"
            f"Format: Just list movie titles numbered 1-15."
        )

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()
        titles = extract_titles(content)

        return titles[:15]

    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return []

def get_fallback_movies(mood, language):

    fallback_movies = {

        "english": {
            "happy": [
                "Forrest Gump","The Pursuit of Happyness","Up","Finding Nemo","Toy Story",
                "La La Land","The Secret Life of Walter Mitty","Paddington 2","Chef",
                "School of Rock","Yes Man","The Intern","Sing Street","Julie & Julia","The Mask"
            ],

            "sad": [
                "The Shawshank Redemption","Titanic","The Green Mile","Schindler's List",
                "A Beautiful Mind","Manchester by the Sea","The Fault in Our Stars",
                "Hachi: A Dog's Tale","Room","The Pianist","Life is Beautiful",
                "Million Dollar Baby","The Boy in the Striped Pajamas","Requiem for a Dream","Seven Pounds"
            ],

            "action": [
                "The Dark Knight","Mad Max Fury Road","John Wick","The Matrix","Gladiator",
                "Inception","Avengers Endgame","Mission Impossible Fallout","Top Gun Maverick",
                "Die Hard","Casino Royale","Terminator 2","Edge of Tomorrow","300","The Raid"
            ],

            "romantic": [
                "The Notebook","Titanic","Casablanca","When Harry Met Sally",
                "The Princess Bride","La La Land","Before Sunrise","Notting Hill",
                "Pride and Prejudice","500 Days of Summer","Me Before You",
                "Crazy Rich Asians","Pretty Woman","Love Actually","The Fault in Our Stars"
            ],

            "funny": [
                "Superbad","Anchorman","Dumb and Dumber","The Hangover","Borat",
                "Step Brothers","The Mask","Rush Hour","Home Alone","Mrs Doubtfire",
                "Johnny English","We're the Millers","21 Jump Street","Yes Man","The Intern"
            ]
        },

        "hindi": [
            "3 Idiots","Dangal","Taare Zameen Par","Queen","Zindagi Na Milegi Dobara",
            "Andhadhun","Pink","PK","Barfi","Lagaan",
            "Dil Chahta Hai","Gully Boy","Bajrangi Bhaijaan","Chak De India","Kabir Singh"
        ],

        "tamil": [
            "Vikram","Master","Kaithi","Enthiran","Sivaji",
            "Asuran","96","Jai Bhim","Ponniyin Selvan",
            "Thuppakki","Mersal","Anniyan","Ghajini","Bigil","Doctor"
        ]
    }

    mood = mood.lower()
    language = language.lower()

    if language == "english":
        return fallback_movies["english"].get(mood, fallback_movies["english"]["happy"])[:15]

    if language in ["hindi", "tamil"]:
        return fallback_movies[language][:15]

    return (
        fallback_movies["english"].get(mood, fallback_movies["english"]["happy"])[:10]
        + fallback_movies["hindi"][:5]
    )

def extract_titles(gpt_output):
    """Extract movie titles from OpenAI response"""
    lines = gpt_output.split("\n")
    titles = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try different patterns
        patterns = [
            r"^\d+\.\s*(.+?)(?:\s+\(|$)",  # "1. Movie Title (year)" or "1. Movie Title"
            r"^\d+\s*-\s*(.+?)(?:\s+\(|$)",  # "1 - Movie Title"
            r"^-\s*(.+?)(?:\s+\(|$)",      # "- Movie Title"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                title = match.group(1).strip()
                # Clean up common suffixes
                title = re.sub(r'\s*\(\d{4}\).*$', '', title)  # Remove (year)
                if title and len(title) > 2:
                    titles.append(title)
                break
    
    return titles

def fetch_movie_info(title):
    """Fetch movie information from OMDB API"""
    params = {
        "t": title,
        "apikey": OMDB_API_KEY,
        "r": "json"
    }
    
    try:
        response = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        data = response.json()
        
        if data.get("Response") != "True":
            print(f"❌ OMDB error for '{title}': {data.get('Error', 'Unknown error')}")
            return None

        # Get streaming platforms
        platforms = get_streaming_platforms(title) if WATCHMODE_API_KEY else ["Netflix", "Amazon Prime"]

        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "poster": data.get("Poster") if data.get("Poster") != "N/A" else None,
            "rating": data.get("imdbRating") if data.get("imdbRating") != "N/A" else "7.5",
            "plot": data.get("Plot") if data.get("Plot") != "N/A" else "No summary available.",
            "genre": data.get("Genre", "Drama"),
            "director": data.get("Director", "Unknown"),
            "actors": data.get("Actors", "Unknown"),
            "language": data.get("Language", "English"),
            "platforms": platforms
        }

    except Exception as e:
        print(f"❌ Error fetching movie info for '{title}': {e}")
        return None

def get_streaming_platforms(title):
    """Get streaming platforms from Watchmode API"""
    if not WATCHMODE_API_KEY:
        return ["Netflix", "Amazon Prime"]
        
    try:
        # Search for the movie
        search_url = "https://api.watchmode.com/v1/search/"
        search_params = {
            "apiKey": WATCHMODE_API_KEY,
            "search_field": "name",
            "search_value": title
        }
        search_resp = requests.get(search_url, params=search_params, timeout=5)
        search_data = search_resp.json()

        if not search_data.get("title_results"):
            return ["Not available"]

        movie_id = search_data["title_results"][0]["id"]

        # Get sources
        sources_url = f"https://api.watchmode.com/v1/title/{movie_id}/sources/"
        sources_params = {"apiKey": WATCHMODE_API_KEY}
        sources_resp = requests.get(sources_url, params=sources_params, timeout=5)
        sources_data = sources_resp.json()

        platforms = sorted(list({src["name"] for src in sources_data if src["type"] == "sub"}))
        return platforms if platforms else ["Not available"]

    except Exception as e:
        print(f"❌ Watchmode error for '{title}': {e}")
        return ["Netflix", "Amazon Prime"]

# # For Render deployment
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("app:app", host="0.0.0.0", port=port)