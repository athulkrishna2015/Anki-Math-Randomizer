import re
import random
from datetime import date

from aqt import mw
from aqt import gui_hooks
from aqt.utils import tooltip
from anki.consts import MODEL_STD

# ==========================================
# CONFIGURATION
# ==========================================

MODEL_NAME = "Math Randomizer (Daily Static)"

# Conflict Groups
CONFLICT_GROUPS = [
    ['I', 'l', '1', '|'], 
    ['O', 'o', '0', 'Q', '\\Theta', '\\theta'], 
    ['v', '\\nu', '\\upsilon'], 
    ['u', '\\mu'], 
    ['w', '\\omega'], 
    ['x', '\\chi', '\\times'], 
    ['p', '\\rho'], 
    ['B', '\\beta'] 
]

# Character Pools
def get_char_range(start, end):
    return [chr(i) for i in range(start, end + 1)]

POOLS = {
    'VL': get_char_range(65, 90),
    'Vl': get_char_range(97, 122),
    'VG': ["\\Gamma", "\\Delta", "\\Theta", "\\Lambda", "\\Xi", "\\Pi", "\\Sigma", "\\Upsilon", "\\Phi", "\\Psi", "\\Omega"],
    'Vg': ["\\alpha", "\\beta", "\\gamma", "\\delta", "\\epsilon", "\\zeta", "\\eta", "\\theta", "\\kappa", "\\lambda", "\\mu", "\\nu", "\\xi", "\\pi", "\\rho", "\\sigma", "\\tau", "\\phi", "\\chi", "\\psi", "\\omega"],
    'VN': [str(i) for i in range(2, 10)]
}
POOLS['VV'] = POOLS['VL'] + POOLS['Vl'] + POOLS['VG'] + POOLS['Vg']

# ==========================================
# CORE LOGIC
# ==========================================

def is_conflict(val1, val2):
    if val1 == val2: return True
    for group in CONFLICT_GROUPS:
        if val1 in group and val2 in group:
            return True
    return False

def get_static_symbols(content):
    used = set()
    # Remove tags to avoid false positives
    clean_content = re.sub(r'(VL|Vl|VG|Vg|VN|VV)\d+', '', content)
    
    # Greek
    greek_pattern = r'\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega)'
    matches = re.findall(greek_pattern, clean_content)
    for m in matches: used.add("\\" + m)
    
    # Latin (remove commands first)
    clean_content = re.sub(r'\\[a-zA-Z]+', '', clean_content)
    latin_matches = re.findall(r'[a-zA-Z]', clean_content)
    for m in latin_matches: used.add(m)
        
    return list(used)

def generate_randomized_content(source_text, existing_static_vars=None):
    if not source_text: return source_text
    
    used_symbols = list(existing_static_vars) if existing_static_vars else get_static_symbols(source_text)
    tags = list(set(re.findall(r'(?:VL|Vl|VG|Vg|VN|VV)\d+', source_text)))
    
    temp_pools = {k: v[:] for k, v in POOLS.items()}
    for k in temp_pools: random.shuffle(temp_pools[k])
        
    assignment_map = {}

    for tag in tags:
        type_match = re.match(r'(VL|Vl|VG|Vg|VN|VV)', tag)
        if not type_match: continue
        p_type = type_match.group(1)
        pool = temp_pools[p_type]
        selected = None
        
        for i, candidate in enumerate(pool):
            conflict = False
            for used in used_symbols:
                if is_conflict(candidate, used):
                    conflict = True; break
            if not conflict:
                selected = candidate; pool.pop(i); break
        
        if selected is None and pool: selected = pool.pop(0)  
        if selected:
            assignment_map[tag] = selected
            used_symbols.append(selected)

    sorted_tags = sorted(assignment_map.keys(), key=len, reverse=True)
    result_text = source_text
    for tag in sorted_tags:
        result_text = result_text.replace(tag, assignment_map[tag])
        
    return result_text

# ==========================================
# TRIGGER LOGIC
# ==========================================

def run_deck_randomization(new_state, old_state):
    # SAFETY CHECK: Only run if entering "review" and Collection is loaded
    if new_state != "review":
        return
    if mw.col is None:
        return

    col = mw.col
    model = col.models.by_name(MODEL_NAME)
    if not model: return

    # 1. Identify Current Deck
    deck_id = col.decks.selected()
    deck = col.decks.get(deck_id)
    if not deck: return
    
    deck_name = deck['name']
    
    # 2. Query for Due/New cards in this deck + subdecks
    query = f'"mid:{model["id"]}" "deck:{deck_name}" (is:due OR is:new OR is:learn)'
    note_ids = col.find_notes(query)
    
    if not note_ids:
        return

    count_updated = 0
    today_str = str(date.today())

    # 3. Process Notes
    for nid in note_ids:
        note = col.get_note(nid)
        
        # Check Daily Limit
        if note['LastUpdate'] == today_str:
            continue

        src_front = note['Source Front']
        src_back = note['Source Back']
        if not src_front: continue

        # Consistency
        static_vars = get_static_symbols(src_front + " " + src_back)
        tags = list(set(re.findall(r'(?:VL|Vl|VG|Vg|VN|VV)\d+', src_front + " " + src_back)))
        
        temp_pools = {k: v[:] for k, v in POOLS.items()}
        for k in temp_pools: random.shuffle(temp_pools[k])
        
        assignment_map = {}
        used_symbols = static_vars[:]
        
        for tag in tags:
            type_match = re.match(r'(VL|Vl|VG|Vg|VN|VV)', tag)
            if not type_match: continue
            p_type = type_match.group(1)
            pool = temp_pools[p_type]
            selected = None
            for i, candidate in enumerate(pool):
                conflict = False
                for used in used_symbols:
                    if is_conflict(candidate, used): conflict = True; break
                if not conflict: selected = candidate; pool.pop(i); break
            
            if selected is None and pool: selected = pool.pop(0)
            if selected:
                assignment_map[tag] = selected
                used_symbols.append(selected)

        # Apply
        final_front = src_front
        final_back = src_back
        for tag in sorted(assignment_map.keys(), key=len, reverse=True):
            final_front = final_front.replace(tag, assignment_map[tag])
            final_back = final_back.replace(tag, assignment_map[tag])

        note['Front'] = final_front
        note['Back'] = final_back
        note['LastUpdate'] = today_str
        col.update_note(note)
        count_updated += 1

    if count_updated > 0:
        # If the current card was just updated, reload the screen
        if mw.reviewer.card and mw.reviewer.card.nid in note_ids:
            mw.reset()
        tooltip(f"Math Randomizer: Randomized {count_updated} cards in '{deck_name}'")

# ==========================================
# SETUP
# ==========================================

def setup_model():
    col = mw.col
    mm = col.models.by_name(MODEL_NAME)
    if not mm:
        mm = col.models.new(MODEL_NAME)
        col.models.add_field(mm, col.models.new_field("Source Front"))
        col.models.add_field(mm, col.models.new_field("Source Back"))
        col.models.add_field(mm, col.models.new_field("Front")) 
        col.models.add_field(mm, col.models.new_field("Back"))  
        col.models.add_field(mm, col.models.new_field("LastUpdate")) 
        t = col.models.new_template("Card 1")
        t['qfmt'] = "{{Front}}"
        t['afmt'] = "{{FrontSide}}\n<hr id=answer>\n{{Back}}"
        col.models.add_template(mm, t)
        mm['css'] = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }"
        col.models.add(mm)

# HOOKS
gui_hooks.profile_did_open.append(setup_model)

# CHANGED: 'state_did_change' fires every time you enter the review screen
gui_hooks.state_did_change.append(run_deck_randomization)