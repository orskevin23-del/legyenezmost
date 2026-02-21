import logging
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)

async def get_top_performing_patterns(user_id: str, top_n: int = 3) -> Dict:
    """
    Get top performing patterns from analytics data.
    Returns top hooks, dominance lines, open loops, and close patterns.
    """
    try:
        # Top hooks by retention
        top_hooks = await db.analytics_data.find(
            {"user_id": user_id},
            {"_id": 0, "hook_title": 1, "retention_hook": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(top_n).to_list(length=top_n)
        
        # Top dominance lines
        top_dominance = await db.analytics_data.find(
            {"user_id": user_id, "dominance_line": {"$ne": None, "$ne": ""}},
            {"_id": 0, "dominance_line": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(top_n).to_list(length=top_n)
        
        # Top open loops
        top_open_loops = await db.analytics_data.find(
            {"user_id": user_id, "open_loop": {"$ne": None, "$ne": ""}},
            {"_id": 0, "open_loop": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(top_n).to_list(length=top_n)
        
        # Top close patterns
        top_closes = await db.analytics_data.find(
            {"user_id": user_id, "close": {"$ne": None, "$ne": ""}},
            {"_id": 0, "close": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(top_n).to_list(length=top_n)
        
        # Top performing full scripts as examples
        top_scripts = await db.analytics_data.find(
            {"user_id": user_id},
            {"_id": 0, "resolve_script": 1, "retention_percent": 1, "likes": 1}
        ).sort("retention_percent", -1).limit(top_n).to_list(length=top_n)
        
        return {
            "top_hooks": top_hooks,
            "top_dominance_lines": top_dominance,
            "top_open_loops": top_open_loops,
            "top_close_patterns": top_closes,
            "top_scripts": top_scripts
        }
    
    except Exception as e:
        logger.error(f"Error getting top performing patterns: {str(e)}")
        return {
            "top_hooks": [],
            "top_dominance_lines": [],
            "top_open_loops": [],
            "top_close_patterns": [],
            "top_scripts": []
        }

def generate_optimized_prompt(
    topic: str,
    keywords: List[str],
    mode: str,
    patterns: Dict
) -> tuple:
    """
    Generate OpenAI prompt enhanced with top performing patterns from analytics.
    """
    keywords_str = ", ".join(keywords) if keywords else "Hoffnung, Glaube, innere Kraft"
    
    # Base system prompt
    system_prompt = (
        "Du schreibst emotionale, Glaubens-basierte YouTube Shorts-Skripte für Menschen, "
        "die Hoffnung und innere Kraft suchen. Deine Skripte sind tief, authentisch, und direkt "
        "vom Herzen. Keine Floskeln, keine künstliche Sprache. Reine emotionale Tiefe."
    )
    
    # Build examples section from analytics data
    examples_section = ""
    
    if patterns.get("top_hooks") and len(patterns["top_hooks"]) > 0:
        examples_section += "\n\n**TOP PERFORMING HOOKS (hohe Retention):**\n"
        for i, hook in enumerate(patterns["top_hooks"][:3], 1):
            retention = hook.get("retention_percent", 0)
            hook_text = hook.get("hook_title", "")
            examples_section += f"{i}. \"{hook_text}\" (Retention: {retention}%)\n"
    
    if patterns.get("top_dominance_lines") and len(patterns["top_dominance_lines"]) > 0:
        examples_section += "\n**TOP DOMINANCE LINES:**\n"
        for i, dom in enumerate(patterns["top_dominance_lines"][:3], 1):
            dom_text = dom.get("dominance_line", "")
            examples_section += f"{i}. \"{dom_text}\"\n"
    
    if patterns.get("top_open_loops") and len(patterns["top_open_loops"]) > 0:
        examples_section += "\n**TOP OPEN LOOPS:**\n"
        for i, loop in enumerate(patterns["top_open_loops"][:3], 1):
            loop_text = loop.get("open_loop", "")
            examples_section += f"{i}. \"{loop_text}\"\n"
    
    if patterns.get("top_close_patterns") and len(patterns["top_close_patterns"]) > 0:
        examples_section += "\n**TOP CLOSE PATTERNS:**\n"
        for i, close in enumerate(patterns["top_close_patterns"][:3], 1):
            close_text = close.get("close", "")
            examples_section += f"{i}. \"{close_text}\"\n"
    
    # Enhanced user prompt with analytics insights
    user_prompt = f"""Du bist ein meisterlicher Drehbuchautor für emotionale, Glaubens-basierte YouTube Shorts in Deutsch.

Thema: {topic}
Schlüsselwörter: {keywords_str}

{examples_section}

**VERWENDE die obigen TOP PERFORMING PATTERNS als Inspiration!**

Erstelle JETZT ein KURZES, emotional tiefes Faith-basiertes Skript:

1. LÄNGE: Maximal 300-350 Zeichen GESAMT (kein längeres!)
2. STRUKTUR: 
   - Hook (verwende einen Stil aus den top performing hooks)
   - Dominance Line (kraftvolle Aussage wie in den Beispielen)
   - Open Loop (schaffe Spannung wie in den top loops)
   - Body (kurze, kraftvolle Botschaft)
   - Close (verwende einen erfolgreichen Close-Stil)

3. OHNE Formatierung, Überschriften oder Markierungen - nur reiner Text zum Vorlesen
4. TON: Spricht direkt ins Herz, hoffnungsvoll, authentisch, tiefgründig
5. RHYTHMUS: Natürliche Pausen zwischen Gedanken (für Stille und Reflexion)
6. HOOK: Muss magnetisch sein wie in den Beispielen (emotional packend, nicht ablenkbar)
7. BODY: Kurz aber kraftvoll, der Kern der Botschaft mit echtem Gefühl

Gib NUR den deutschen Scripttext zurück. Nichts anderes."""
    
    return system_prompt, user_prompt
