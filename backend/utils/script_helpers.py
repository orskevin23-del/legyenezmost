import re
from typing import Tuple, List

def extract_hook_from_script(script_text: str) -> str:
    """
    Extract first sentence as hook from script.
    Splits by punctuation: . ! ?
    """
    pattern = r'[.!?]+'
    segments = re.split(pattern, script_text)
    
    for segment in segments:
        segment = segment.strip()
        if segment:
            return segment
    
    # Fallback: return first 100 chars
    return script_text[:100]

def detect_hook_type_and_tags(hook_text: str, topic: str) -> Tuple[str, str, List[str]]:
    """
    Auto-detect hook type, mode, and tags based on content.
    
    Returns: (hook_type, mode, tags_list)
    """
    hook_lower = hook_text.lower()
    topic_lower = topic.lower() if topic else ""
    
    # Detect hook type
    hook_type = "emotional_trigger"  # Default for Faith niche
    
    if any(word in hook_lower for word in ["hast du", "merkst du", "siehst du", "weißt du", "fühlst du"]):
        hook_type = "identity_filter"
    elif any(word in hook_lower for word in ["jetzt", "sofort", "schnell", "moment"]):
        hook_type = "urgency"
    elif any(word in hook_lower for word in ["nicht für alle", "nicht für dich", "nicht jeder"]):
        hook_type = "not_for_everyone"
    elif any(word in hook_lower for word in ["nicht", "kein", "gegenteil"]):
        hook_type = "reverse_psychology"
    elif any(word in hook_lower for word in ["fühlt", "spürst", "herz", "seele", "tief"]):
        hook_type = "emotional_trigger"
    
    # Detect mode
    mode = "FAITH_EXPLICIT"  # Default
    if any(word in hook_lower for word in ["bist", "wirklich", "zustand"]):
        mode = "STATE_BASED"
    
    # Tags dictionary
    tags_dict = {
        "hoffnung": "Hoffnung",
        "glaube": "Glaube",
        "gott": "Gott",
        "kraft": "Kraft",
        "stärke": "Stärke",
        "liebe": "Liebe",
        "vertrauen": "Vertrauen",
        "sinn": "Sinn",
        "seele": "Seele",
        "herz": "Herz",
        "innerfrieden": "Innerer Friede",
        "innere ruhe": "Innere Ruhe",
        "faith": "Glaube",
        "hope": "Hoffnung",
        "strength": "Kraft",
        "purpose": "Zweck",
        "meaning": "Sinn",
        "spirit": "Geist",
        "dominance": "Dominanz",
        "open loop": "Offene Schleife"
    }
    
    # Detect tags from hook and topic
    detected_tags = []
    combined_text = f"{hook_lower} {topic_lower}"
    
    for keyword, tag in tags_dict.items():
        if keyword in combined_text:
            if tag not in detected_tags:
                detected_tags.append(tag)
    
    # Default tags if none detected
    if not detected_tags:
        detected_tags = ["Glaube", "Hoffnung"]
    
    return (hook_type, mode, detected_tags)

def count_characters(text: str) -> int:
    """Count characters in text."""
    return len(text)

def truncate_to_length(text: str, max_length: int = 350) -> str:
    """
    Truncate text to max length while maintaining sentence integrity.
    Cuts at last sentence boundary if possible.
    """
    if len(text) <= max_length:
        return text
    
    # Find last sentence boundary before max_length
    truncated = text[:max_length]
    last_punct = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_punct > 0:
        return truncated[:last_punct + 1]
    else:
        # No sentence boundary, just cut at max_length
        return truncated + "."

def generate_german_script_prompt(topic: str, keywords: List[str], mode: str) -> str:
    """
    Generate OpenAI prompt for German Faith-niche scripts.
    """
    keywords_str = ", ".join(keywords) if keywords else "Hoffnung, Glaube, innere Kraft"
    
    system_prompt = (
        "Du schreibst emotionale, Glaubens-basierte YouTube Shorts-Skripte für Menschen, "
        "die Hoffnung und innere Kraft suchen. Deine Skripte sind tief, authentisch, und direkt "
        "vom Herzen. Keine Floskeln, keine künstliche Sprache. Reine emotionale Tiefe."
    )
    
    user_prompt = f"""Du bist ein meisterlicher Drehbuchautor für emotionale, Glaubens-basierte YouTube Shorts in Deutsch.

Thema: {topic}
Schlüsselwörter: {keywords_str}

Erstelle JETZT ein KURZES, emotional tiefes Faith-basiertes Skript:

1. LÄNGE: Maximal 300-350 Zeichen GESAMT (kein längeres!)
2. STRUKTUR: Hook (emotional fesselnd) + Body (kurze, kraftvolle Botschaft)
3. OHNE Formatierung, Überschriften oder Markierungen - nur reiner Text zum Vorlesen
4. TON: Spricht direkt ins Herz, hoffnungsvoll, authentisch, tiefgründig
5. RHYTHMUS: Natürliche Pausen zwischen Gedanken (für Stille und Reflexion)
6. HOOK: Muss magnetisch sein, emotional packend, nicht ablenkbar
7. BODY: Kurz aber kraftvoll, der Kern der Botschaft mit echtem Gefühl

Gib NUR den deutschen Scripttext zurück. Nichts anderes."""
    
    return system_prompt, user_prompt