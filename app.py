from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import os
import re as regex
from datetime import datetime

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Read HTML from index.html to keep it clean
with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r') as f:
    HTML_TEMPLATE = f.read()

def query_ollama(prompt):
    """Query Ollama using the HTTP API. Returns None if Ollama is not available."""
    try:
        import urllib.request
        import urllib.error
        
        url = "http://localhost:11434/api/generate"
        data = json.dumps({
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            output = result.get('response', '').strip()
            if output:
                return {"response": output}
        return None
    except Exception:
        return None


def get_mock_response(resume, jd):
    return {
        "match_score": "78%",
        "missing_keywords": ["Kubernetes", "AWS Lambda", "PostgreSQL optimization"],
        "improvement_suggestions": [
            "Quantify achievements with specific metrics",
            "Highlight PostgreSQL expertise and database optimization",
            "Include cloud architecture and deployment pipeline details"
        ],
        "rewritten_bullet": "Architected and deployed a scalable REST API serving 150K+ daily active users, implementing Redis caching and PostgreSQL query optimization that reduced average response time from 250ms to 85ms (66% improvement)",
        "note": "Mock response (Ollama not available)"
    }

def parse_ollama_response_v2(text, resume, jd):
    import re
    result = {"match_score": "0%", "missing_keywords": [], "improvement_suggestions": [], "rewritten_bullet": ""}
    lines = text.split('\n')
    current_section = None
    for line in lines:
        ls = line.strip()
        if not ls:
            continue
        if 'MATCH_SCORE' in ls.upper() or 'match_score' in ls.lower():
            nums = regex.findall(r'\d+', ls)
            if nums:
                result["match_score"] = nums[0] + '%'
        pct = regex.search(r'(\d{1,3})%', ls)
        if pct and result["match_score"] == "0%":
            result["match_score"] = pct.group(0)
        lu = ls.upper()
        if any(w in lu for w in ['MISSING', 'KEYWORD', 'LACKING']):
            current_section = 'keywords'
        elif any(w in lu for w in ['IMPROVEMENT', 'SUGGESTION', 'IMPROVE']):
            current_section = 'suggestions'
        elif any(w in lu for w in ['REWRITE', 'BULLET', 'REWRITTEN']):
            current_section = 'bullet'
        elif any(w in lu for w in ['CONCLUSION', 'SUMMARY']) and current_section != 'bullet':
            current_section = None
        if current_section in ['keywords', 'suggestions']:
            cl = re.sub(r'^[-•*\d\.\)]\s*', '', ls)
            if any(h in cl.upper() for h in ['MISSING', 'KEYWORD', 'IMPROVEMENT', 'SUGGEST']):
                cl = ''
            if cl and len(cl) > 10:
                tgt = result["missing_keywords"] if current_section == 'keywords' else result["improvement_suggestions"]
                limit = 10 if current_section == 'keywords' else 5
                if cl not in tgt and len(tgt) < limit:
                    tgt.append(cl)
        elif current_section == 'bullet':
            if len(ls) < 30 or any(h in lu for h in ['REWRITE', 'BULLET']):
                continue
            if not result["rewritten_bullet"] and len(ls) > 30:
                result["rewritten_bullet"] = ls
    if not result["rewritten_bullet"] or result["match_score"] == "0%":
        for sent in re.split(r'[.!?]+', text):
            s = sent.strip()
            if re.search(r'\d+%|\d+k|\d+[KM]|million|thousand|reduced.*[0-9]', s, re.I):
                if len(s) > 30 and not result["rewritten_bullet"]:
                    result["rewritten_bullet"] = s
                    break
    if not result["improvement_suggestions"]:
        result["improvement_suggestions"] = ["Review alignment between resume and job requirements"]
    if not result["rewritten_bullet"]:
        result["rewritten_bullet"] = "See suggestions above for bullet point improvements"
    if not result["missing_keywords"]:
        result["missing_keywords"] = ["Review job description for specific technical requirements"]
    return result


@application.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@application.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume = data.get('resume', '')
    jd = data.get('jd', '')
    if not resume or not jd:
        return jsonify({"error": "Both resume and job description are required"}), 400
    prompt = f"""Compare these resume and job description. Provide structured output:
MATCH_SCORE: [0-100]
MISSING_KEYWORDS:
- keyword
IMPROVEMENT_SUGGESTIONS:
- suggestion
REWRITTEN_BULLET:
[bullet]
Resume: {resume}
Job Description: {jd}"""
    ollama_result = query_ollama(prompt)
    if ollama_result and 'response' in ollama_result:
        parsed = parse_ollama_response_v2(ollama_result['response'], resume, jd)
        return jsonify(parsed)
    elif ollama_result and isinstance(ollama_result, dict):
        return jsonify(ollama_result)
    mock = get_mock_response(resume, jd)
    mock['note'] = 'Mock response (Ollama not available)'
    return jsonify(mock)


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5001)
