from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from app.search import search
from app.models import Participant, Criminal, User, Case
from app.utils import station_scoped
from rapidfuzz import process, fuzz
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate
import re

def detect_script(text):
    # Simple check for Devanagari range
    for char in text:
        if '\u0900' <= char <= '\u097f':
            return 'devanagari'
    return 'latin'

def validate_input(q):
    """
    Validates search input.
    - length >= 2
    - no dangerous characters (basic injection prevention, though ORM handles SQL)
    """
    if not q or len(q) < 2:
        return False
    # Allow alphanumeric, spaces, and Devanagari. Reject obvious script/html tags.
    if re.search(r'[<>{}]', q):
        return False
    return True

@search.route('/search_name', methods=['GET'])
@login_required
def search_name():
    q = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 10))
    threshold = int(request.args.get('threshold', 60))
    
    if not validate_input(q):
        return jsonify({'results': []})
        
    # Transliteration Logic
    query_variations = {q}
    if detect_script(q) == 'devanagari':
        # Transliterate Hindi to English (ITRANS or HK)
        transliterated = transliterate(q, sanscript.DEVANAGARI, sanscript.HK)
        query_variations.add(transliterated)
    
    # Fetch Candidates (Scoped to Station)
    candidates = []
    
    # 1. Cases & Incidents (Case Number, Title, Description, Location)
    cases = station_scoped(Case.query).all()
    for c in cases:
        # Case Number (High value)
        candidates.append({
            'name': c.case_number,
            'source': 'Case',
            'id': c.id,
            'details': c.title,
            'url': f"/cases/{c.id}"
        })
        # Title
        candidates.append({
            'name': c.title,
            'source': 'Case Title',
            'id': c.id,
            'details': f"#{c.case_number}",
            'url': f"/cases/{c.id}"
        })
        # Incident / Offense
        if c.offense_type:
            candidates.append({
                'name': c.offense_type,
                'source': 'Incident Type',
                'id': c.id,
                'details': f"Case #{c.case_number}",
                'url': f"/cases/{c.id}"
            })
        # Location
        if c.location:
             candidates.append({
                'name': c.location,
                'source': 'Incident Location',
                'id': c.id,
                'details': f"Case #{c.case_number}",
                'url': f"/cases/{c.id}"
            })

    # 2. Suspects (Criminals)
    criminals = station_scoped(Criminal.query).all()
    for c in criminals:
        candidates.append({
            'name': c.name,
            'source': 'Suspect/Criminal',
            'id': c.id,
            'details': f"Status: {c.status}",
            'url': f"/criminals/{c.id}" # Placeholder
        })
        if c.aliases:
            candidates.append({
                'name': c.aliases,
                'source': f'Alias ({c.name})',
                'id': c.id,
                'details': f"Status: {c.status}",
                'url': f"/criminals/{c.id}"
            })
            
    # 3. Names (Participants)
    # Join with Case to scope properly
    participants = Participant.query.join(Case).filter(Case.station_id == current_user.station_id).all()
    for p in participants:
         # Find associated case
         case = Case.query.get(p.case_id)
         candidates.append({
            'name': p.name,
            'source': f'{p.type} (Name)',
            'id': p.id,
            'details': f"Case: {case.case_number if case else 'Unknown'}",
            'url': f"/cases/{p.case_id}"
         })
         
    # 4. Names (Officers/Users)
    users = station_scoped(User.query).all()
    for u in users:
        candidates.append({
            'name': u.full_name,
            'source': f'Officer ({u.role})',
            'id': u.id,
            'details': u.badge_number,
            'url': f"/admin/users" 
        })

    # Fuzzy Matching
    results = []
    
    # Extract names for RapidFuzz
    # Ensure all names are strings
    choices = [str(c['name']) for c in candidates]
    
    matched_indices = set()
    
    for query_var in query_variations:
        # returns list of (match, score, index)
        # We lower the limit for extraction to optimize, then sort manually
        matches = process.extract(query_var, choices, scorer=fuzz.WRatio, limit=None)
        
        for name, score, idx in matches:
            if score >= threshold:
                if idx not in matched_indices:
                    res = candidates[idx].copy()
                    res['score'] = score
                    results.append(res)
                    matched_indices.add(idx)
    
    # Sort by score desc, then by source priority (Case > Suspect > Name)
    # Just Score is distinct usually.
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({'results': results[:limit]})
