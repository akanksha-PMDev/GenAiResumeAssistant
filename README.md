# GenAI Resume Assistant

A modern, professional resume analysis tool that uses local AI (Ollama) to compare your resume against a job description. Built with Python Flask, featuring PDF upload support and a sleek dark-mode interface.

## Features

- **PDF Upload**: Drag & drop or click to upload PDF resumes and job descriptions
- **Match Score**: Visual circular progress indicator showing percentage match
- **Missing Keywords**: Tagged list of skills/technologies from JD not in your resume
- **3 Improvement Suggestions**: Actionable tips to strengthen your application
- **Rewritten Bullet Point**: AI-generated, quantified bullet point with measurable impact
- **Modern Dark UI**: Tailwind CSS powered, glass-morphism design with smooth animations
- **Local AI Processing**: All analysis happens locally via Ollama (or mock mode)

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JS + Tailwind CSS (CDN)
- **AI**: Ollama (mistral/llama2) or mock responses
- **Design**: Dark theme, glass-morphism, smooth animations

## Installation

### 1. Install Python Dependencies

```bash
pip3 install flask --break-system-packages
```

### 2. Install Ollama (Optional but Recommended)

For real AI analysis, install Ollama locally:

**macOS:**
```bash
brew install ollama
ollama serve &
ollama pull mistral
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull mistral
```

**Windows:**
Download from https://ollama.com/

## How to Run

```bash
python3 app.py
```

Open your browser to: **http://localhost:5001**

## Usage

### Method 1: PDF Upload (Recommended)
1. Click the upload zone or drag & drop your PDF resume (left panel)
2. Upload your job description PDF (right panel)
3. Click "Analyze Match"
4. View results with visual score and suggestions

### Method 2: Direct Text Input
1. Paste your resume text in the left text area (pre-filled with sample)
2. Paste the job description in the right text area
3. Click "Analyze Match"
4. View detailed analysis results

## Features Explained

### Match Score
A circular progress indicator (0-100%) showing how well your resume matches the job requirements:
- **80-100%** (Green): Excellent match
- **60-79%** (Amber): Good match, minor improvements needed
- **0-59%** (Red): Significant revisions recommended

### Missing Keywords
Skills and technologies mentioned in the job description but not found in your resume. Add these to increase your match score.

### Improvement Suggestions
Three actionable tips to strengthen your resume, such as:
- Adding specific metrics and percentages
- Highlighting relevant technical expertise
- Including relevant project or deployment details

### Rewritten Bullet Point
An AI-generated, quantified resume bullet point showing measurable impact. Use this as inspiration for rewriting your own bullet points.

## Files

- **app.py** - Flask backend with Ollama integration, PDF upload support
- **index.html** - Standalone frontend (also embedded in app.py)
- **README.md** - This file

## API Endpoints

### `GET /`
Serves the main HTML page.

### `POST /analyze`
Analyze resume against job description.

**Request:**
```json
{
  "resume": "Your resume text...",
  "jd": "Job description text..."
}
```

**Response:**
```json
{
  "match_score": "78%",
  "missing_keywords": ["Kubernetes", "AWS Lambda"],
  "improvement_suggestions": ["Tip 1", "Tip 2", "Tip 3"],
  "rewritten_bullet": "Architected and deployed...",
  "note": "Optional status message"
}
```

## Customization

### Change Ollama Model
Edit `query_ollama()` in `app.py`:
```python
result = subprocess.run(
    ["ollama", "run", "llama2", ...]  # Change "mistral" to your model
```

### Adjust Port
If port 5001 is in use, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```

## PDF Upload Note

The current implementation includes file upload UI with PDF validation. For production use with actual PDF text extraction, integrate one of:

- **pdf.js** (client-side): https://mozilla.github.io/pdf.js/
- **PyPDF2** or **pdfplumber** (server-side): Parse PDFs in Flask

## Troubleshooting

**Ollama not responding:**
```bash
ollama serve &
ollama pull mistral
```

**Port 5001 already in use:**
```bash
lsof -ti:5001 | xargs kill -9
# Or change port in app.py
```

**Mock mode active:**
The app automatically uses mock responses if Ollama is unavailable. This lets you test the UI immediately after installing Flask.

## UI Features

- **Dark theme** with blue/teal accents
- **Glass-morphism** cards with backdrop blur
- **Animated score ring** with smooth progress
- **Drag & drop** file upload with visual feedback
- **Character counters** for text areas
- **Responsive design** (mobile-friendly)
- **Staggered animations** on result cards
- **Reduced motion** support for accessibility

## License

MIT - Free to use and modify