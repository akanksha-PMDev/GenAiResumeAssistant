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
    """Generate realistic mock response based on resume-JD keyword matching."""
    resume_lower = resume.lower()
    jd_lower = jd.lower()
    
    # Key technical keywords to check
    tech_keywords = {
        'python': 2, 'django': 3, 'flask': 2, 'postgresql': 3, 'mysql': 2,
        'aws': 3, 'docker': 2, 'kubernetes': 3, 'redis': 2, 'javascript': 2,
        'react': 2, 'node': 2, 'typescript': 2, 'mongodb': 2, 'git': 1,
        'ci/cd': 2, 'kafka': 3, 'elasticsearch': 3, 'terraform': 3,
        'microservices': 3, 'rest': 1, 'api': 1, 'graphql': 2,
        'machine learning': 3, 'tensorflow': 3, 'pytorch': 3, 'scikit': 2,
        'pandas': 2, 'numpy': 2, 'sql': 2, 'nosql': 2
    }
    
    # Check experience keywords
    exp_keywords = {
        'years': 1, 'experience': 1, 'led': 2, 'team': 2, 'mentor': 2,
        'senior': 2, 'junior': 1, 'architect': 3, 'manager': 2,
        'scaled': 3, 'millions': 3, 'users': 1, 'performance': 2,
        'optimized': 2, 'reduced': 2, 'improved': 2, 'increased': 2,
        'designed': 2, 'implemented': 2, 'deployed': 2, 'built': 1,
        'maintained': 1, 'debugged': 1, 'tested': 1
    }
    
    # Calculate matches
    matched_keywords = []
    missing_keywords = []
    resume_score = 0
    max_score = 0
    
    for keyword, weight in tech_keywords.items():
        max_score += weight
        if keyword in resume_lower:
            resume_score += weight
            matched_keywords.append(keyword)
        elif keyword in jd_lower:
            missing_keywords.append(keyword.title())
    
    exp_score = 0
    for keyword, weight in exp_keywords.items():
        if keyword in resume_lower:
            exp_score += weight
    
    # Calculate percentage (cap at 95%)
    if max_score > 0:
        tech_match = (resume_score / max_score) * 70  # Tech = 70% of score
        exp_match = min((exp_score / 15) * 30, 30)     # Exp = 30% of score
        match_pct = min(int(tech_match + exp_match), 95)
    else:
        match_pct = 50
    
    # If JD asks for things not in resume, deduct
    if missing_keywords:
        deduction = min(len(missing_keywords) * 3, 25)
        match_pct = max(match_pct - deduction, 10)
    
    # Generate improvement suggestions based on missing items
    suggestions = []
    if missing_keywords:
        # Only add up to 3 context-aware suggestions
        added = 0
        for kw in missing_keywords[:3]:
            if added >= 3:
                break
            kw_lower = kw.lower()
            if added < 3 and any(f in kw_lower for f in ['python', 'django', 'flask', 'framework']):
                suggestions.append("Highlight Python framework experience (Django/Flask) and REST API development")
                added += 1
            elif added < 3 and any(f in kw_lower for f in ['postgresql', 'mysql', 'database', 'sql']):
                suggestions.append("Include database experience (PostgreSQL, MySQL) and query optimization")
                added += 1
            elif added < 3 and any(f in kw_lower for f in ['aws', 'cloud', 'docker', 'kubernetes']):
                suggestions.append("Mention cloud deployment and containerization experience")
                added += 1
            elif added < 3 and any(f in kw_lower for f in ['performance', 'redis', 'optimize']):
                suggestions.append("Quantify performance improvements with metrics")
                added += 1
    
    if not suggestions:
        suggestions = [
            "Add specific metrics to quantify achievements",
            "Include links to portfolio or GitHub repositories"
        ]
    
    # Ensure exactly 3 suggestions
    while len(suggestions) < 3:
        extras = [
            "Review alignment between resume bullets and job requirements",
            "Quantify achievements with specific metrics and impact",
            "Include relevant technical keywords from the job description"
        ]
        for s in extras:
            if s not in suggestions:
                suggestions.append(s)
                if len(suggestions) >= 3:
                    break
    
    # Generate rewritten bullet with metrics
    bullet_templates = [
        "Designed and implemented scalable systems serving {users}+ users, improving performance by {pct}% through {tech} optimization",
        "Led a team of {team} engineers to deliver {project}, resulting in {impact}% improvement in {metric}",
        "Architected {system} using {tech}, reducing latency from {old}ms to {new}ms ({pct}% improvement)",
        "Built and deployed {feature} handling {volume} requests/day with {tech}, achieving {uptime}% uptime"
    ]
    
    import random
    template = random.choice(bullet_templates)
    rewritten = template.format(
        users=random.choice(["100K", "50K", "250K", "1M"]),
        pct=random.choice([30, 40, 50, 60]),
        tech=random.choice(["Redis caching", "database queries", "API endpoints"]),
        team=random.choice(["3", "5", "8"]),
        project=random.choice(["microservices platform", "data pipeline", "API gateway"]),
        impact=random.choice([25, 35, 50, 60]),
        metric=random.choice(["response time", "throughput", "efficiency"]),
        system=random.choice(["REST API", "data processing pipeline", "event-driven system"]),
        old=random.choice([200, 250, 300]),
        new=random.choice([80, 85, 100, 120]),
        feature=random.choice(["authentication service", "payment processing", "real-time notifications"]),
        volume=random.choice(["10K", "50K", "100K"]),
        uptime=random.choice(["99.9", "99.95", "99.99"])
    )
    
    # Cap match score at what we actually found
    if len(matched_keywords) == 0 and 'python' not in resume_lower.lower():
        match_pct = min(match_pct, 40)
    
    return {
        "match_score": f"{match_pct}%",
        "missing_keywords": missing_keywords[:5] if missing_keywords else ["Strong alignment - no major gaps detected"],
        "improvement_suggestions": suggestions,
        "rewritten_bullet": f"- {rewritten}",
        "note": f"Mock analysis based on keyword matching (Ollama not available in this environment)"
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
                limit = 10 if current_section == 'keywords' else 3
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
    
    # On Vercel or when Ollama is not available, use mock responses
    # Vercel sets VERCEL environment variable, or check for Ollama availability
    use_mock = os.environ.get('VERCEL') is not None or os.environ.get('USE_MOCK') == 'true'
    
    if not use_mock:
        try:
            ollama_result = query_ollama(prompt)
            if ollama_result and 'response' in ollama_result:
                import re
                # Quick check: if response looks like HTML (Vercel error), fallback
                if ollama_result['response'].strip().startswith('<!DOCTYPE'):
                    use_mock = True
                else:
                    parsed = parse_ollama_response_v2(ollama_result['response'], resume, jd)
                    return jsonify(parsed)
        except Exception:
            use_mock = True
    
    # Use mock response (works everywhere including Vercel)
    mock = get_mock_response(resume, jd)
    mock['note'] = 'Mock analysis (Ollama not available in this environment)'
    return jsonify(mock)


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)
