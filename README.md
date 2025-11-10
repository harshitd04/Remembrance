# Remembrance: Voice Journaling Application

A sophisticated voice journaling web application that converts speech to text, stores entries with semantic search capabilities, and generates hierarchical AI summaries.

## Features

### Core Functionality
- **Voice Recording**: Real-time transcription using OpenAI Whisper-1
- **File Upload**: Audio file transcription using Whisper-1 model
- **Text Journaling**: Direct text entry support
- **Dual Search**: Keyword-based and AI-powered semantic search
- **AI Summaries**: Automated weekly, monthly, and yearly summaries
- **Multi-User Support**: Complete data isolation per user with folder-based storage

### User Interface
- Crystal neon violet space theme with glass-morphism effects
- Fully responsive design (mobile, tablet, desktop)
- Real-time recording indicators
- Intuitive navigation and controls
- User management via Settings page

## Technology Stack

- **Backend Framework**: Flask (Python 3.9+)
- **AI Services**: 
  - OpenAI Whisper-1 (speech-to-text transcription)
  - OpenAI GPT-4o Mini (summarization)
  - OpenAI Text-Embedding-3-Small (semantic search)
- **RAG Framework**: LangChain
- **Data Storage**: JSON files with hierarchical structure
- **Frontend**: Vanilla JavaScript with custom CSS
- **Task Scheduling**: APScheduler

## Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- pip package manager

### Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. Initialize data directories:
   ```bash
   python setup.py
   ```

4. Run the application:
   ```bash
   python run.py
   ```

5. Access the application:
   
   Open your browser and navigate to `http://localhost:5000`

## Multi-User System

### Overview
Remembrance supports multiple users with complete data isolation. Each user has their own separate:
- Journal entries
- Embeddings (for semantic search)
- Summaries (weekly, monthly, yearly)

### Managing Users

**Access Settings:**
- Click on your username in the top-right navigation (👤 Username)
- Or navigate to the Settings page from the menu

**Add New User:**
1. Go to Settings page
2. Enter the user's name (e.g., "Derek", "Clair")
3. Click "Add User"
4. System automatically creates their folder structure

**Switch Between Users:**
1. Go to Settings page
2. Click "Switch" next to the user you want to switch to
3. All pages will now show that user's data

**Current User Display:**
- Always visible in the top navigation bar (👤 Username)
- Click on it to go to Settings
- Active user marked on Settings page

### Data Structure
```
data/
├── users.json              # User registry
├── harshit/                # Harshit's data (default user)
│   ├── entries/
│   ├── embeddings/
│   ├── summaries/
│   └── temp/
├── derek/                  # Derek's data
│   ├── entries/
│   ├── embeddings/
│   ├── summaries/
│   └── temp/
└── clair/                  # Clair's data
    ├── entries/
    ├── embeddings/
    ├── summaries/
    └── temp/
```

### Fresh Installation
The system automatically creates the "harshit" user as the default user on first run. You can add more users through the Settings page.

## Usage

### Viewing Journal Entries

**Journals Page:**
1. Navigate to the Journals page from the menu
2. Select a date using the date picker or quick buttons (Today, Yesterday, Last Week)
3. View all entries for that date
4. Each entry shows:
   - Date and time created
   - Full content
   - Entry type (voice or text)
   - Edit history if applicable

### Creating Journal Entries

**Via Voice Recording:**
1. Click the microphone button on the home page
2. Speak your thoughts (maximum 15 minutes)
3. Click the button again to stop recording
4. The audio is automatically transcribed using OpenAI Whisper
5. Review and edit the transcription if needed
6. Select a date and click "Save Entry"

**Via File Upload:**
1. Click "Choose File" to select an audio file
2. Supported formats: MP3, WAV, M4A, WEBM, MP4, MPGA, MPEG
3. Maximum file size: 25MB
4. The file is transcribed using OpenAI Whisper
5. Review the transcription and save

**Via Text Entry:**
1. Type directly into the text area
2. Select a date
3. Click "Save Entry"

### Searching Entries

**Keyword Search:**
- Enter specific words or phrases
- Results show exact matches with highlighted keywords
- Sorted by date (most recent first)

**Semantic Search:**
- Enter natural language questions
- AI analyzes meaning and context
- Returns relevant entries with similarity scores
- Includes AI-generated summary of findings

### Viewing Summaries

- **Weekly Summaries**: Generated every Sunday at midnight (includes date range for easy selection)
- **Monthly Summaries**: Generated on the 1st of each month
- **Yearly Summaries**: Generated on January 1st
- All summaries are created using GPT-4o Mini with batch API for cost optimization
- Each user gets their own separate summaries

**Summary Format:**
All summaries are returned in a structured markdown format with clear sections:
- **Weekly**: Key Emotions, Accomplishments, Challenges, Themes, Insights
- **Monthly**: Overview, Developments, Growth, Challenges, Highlights, Looking Forward
- **Yearly**: Life Trajectory, Milestones, Growth, Challenges, Relationships, Progress, Health, Learnings, Future

## Project Structure

```
remembrance/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration management
│   ├── routes/                  # API endpoints
│   │   ├── main_bp.py          # Home and transcription
│   │   ├── journal_bp.py       # Entry management
│   │   ├── search_bp.py        # Search functionality
│   │   ├── summary_bp.py       # Summary generation
│   │   └── settings_bp.py      # User management
│   ├── services/                # Business logic
│   │   ├── transcription_service.py
│   │   ├── embedding_service.py
│   │   ├── summary_service.py
│   │   ├── rag_service.py
│   │   ├── json_storage_service.py
│   │   └── user_service.py     # User management
│   ├── utils/                   # Helper functions
│   ├── templates/               # HTML templates
│   └── static/                  # CSS and JavaScript
├── data/                        # Multi-user JSON storage
│   ├── users.json              # User registry
│   ├── harshit/                # Default user
│   │   ├── entries/
│   │   ├── summaries/
│   │   └── embeddings/
│   └── [other users]/          # Additional users
├── jobs/                        # Scheduled tasks
├── logs/                        # Application logs
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

## API Endpoints

### Transcription
- `POST /api/transcribe` - Transcribe audio (auto-routes to appropriate model)

### Journal Entries
- `POST /journal/new-entry` - Create new entry
- `GET /journal/entries/{date}` - Retrieve entries by date
- `PUT /journal/edit/{date}` - Edit existing entry
- `DELETE /journal/{date}` - Delete entry

### Search
- `POST /search/keyword` - Keyword-based search
- `POST /search/semantic` - Semantic search with RAG

### Summaries
- `GET /summary/weekly/{week}/{year}` - Get weekly summary (includes date range)
- `GET /summary/monthly/{month}/{year}` - Get monthly summary
- `GET /summary/yearly/{year}` - Get yearly summary

### User Management
- `GET /settings/` - Settings page
- `GET /settings/api/users` - List all users
- `POST /settings/api/users` - Add new user
- `DELETE /settings/api/users/{username}` - Delete user
- `POST /settings/api/users/switch` - Switch active user

## Cost Estimation

### Per Active User (Monthly)
| Service | Usage | Cost |
|---------|-------|------|
| Whisper-1 | 60 min audio | ~$0.36 |
| Text-Embedding-3-Small | ~100 embeddings | ~$0.02 |
| GPT-4o Mini Summaries | 52 weekly + 12 monthly + 1 yearly | ~$0.50 |
| Batch API Discount | 50% off summaries | -$0.25 |
| **Total** | | **~$0.63/month** |

### Scaling
- 10 users: ~$6/month
- 100 users: ~$60/month
- 1000 users: ~$600/month

## Configuration

### Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Data Storage Paths
DATA_DIR=./data
ENTRIES_DIR=./data/entries
SUMMARIES_DIR=./data/summaries
EMBEDDINGS_DIR=./data/embeddings

# Batch Processing Configuration
BATCH_PROCESSING_ENABLED=True
BATCH_PROCESS_TIME=02:00

# Application Settings
MAX_RECORDING_DURATION=900
MAX_FILE_SIZE=26214400
```

## Development

### Running in Development Mode
```bash
python run.py
```

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
- Follows PEP 8 conventions
- Type hints for function parameters
- Comprehensive docstrings

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Security Considerations
- Store API keys in environment variables only
- Use HTTPS in production
- Implement rate limiting
- Enable CORS properly
- Regular security audits

## Troubleshooting

### Common Issues

**Module not found errors:**
```bash
pip install -r requirements.txt
```

**OpenAI API key not found:**
- Verify `.env` file exists
- Check API key is correctly formatted
- Ensure no extra spaces or quotes

**Port 5000 already in use:**
- Change port in `run.py`
- Or kill the process using port 5000

**Audio recording not working:**
- Check browser microphone permissions
- Use HTTPS in production (required by browsers)
- Verify browser compatibility

**Entries not showing after switching users:**
- Make sure you've selected the correct user in Settings
- Verify you're looking at the correct user (check top-right of navigation)
- Each user has completely separate data in `data/{username}/` folders


