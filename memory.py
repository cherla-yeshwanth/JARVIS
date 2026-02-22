"""
JARVIS v1.0 — Memory System
Long-term persistent memory with:
  - Short-term context (last N exchanges in RAM)
  - Fact memory (SQLite — explicit user facts)
  - Episode memory (ChromaDB — semantic search over conversations)
  - Pattern memory (SQLite — tracks usage patterns)
  - LLM-powered fact extraction
"""

import sqlite3
import json
import requests
import os
from datetime import datetime
from typing import List, Optional, Tuple
from config import (
    DB_PATH,
    CHROMA_DIR,
    OLLAMA_HOST,
    FAST_MODEL,
    EMBED_MODEL,
    MAX_SHORT_TERM,
    MAX_SEMANTIC_RESULTS,
    PRIVACY_MODE,
    DATA_DIR,
)

class Memory:
    """Unified memory system combining structured and semantic storage."""

    def __init__(self):
        self.db_path = str(DB_PATH)
        self.privacy_mode = PRIVACY_MODE
        self.short_term: List[dict] = []
        self.max_short_term = MAX_SHORT_TERM

        # Initialize SQLite
        self._init_db()

        # Initialize ChromaDB
        try:
            import chromadb
            self.chroma = chromadb.PersistentClient(path=CHROMA_DIR)
            self.episodes = self.chroma.get_or_create_collection(
                name='episodes',
                metadata={'hnsw:space': 'cosine'}
            )
            self.chroma_available = True
            print(f"[MEMORY] ChromaDB loaded. Episodes: {self.episodes.count()}")
        except Exception as e:
            self.chroma_available = False
            print(f"[MEMORY] ChromaDB not available: {e}")

        print(f"[MEMORY] SQLite loaded. Facts: {self._count_facts()}, Conversations: {self._count_conversations()}")

    def _init_db(self):
        """Initialize SQLite tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    response TEXT NOT NULL,
                    intent TEXT,
                    model_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    hour_of_day INTEGER,
                    day_of_week INTEGER,
                    count INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(task_type, hour_of_day, day_of_week)
                );

                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    trigger_time DATETIME,
                    is_done INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()

    def _count_facts(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute('SELECT COUNT(*) FROM facts').fetchone()[0]
        return count

    def _count_conversations(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
        return count

    def _embed(self, text: str) -> Optional[List[float]]:
        """Get embedding vector from Ollama."""
        try:
            resp = requests.post(
                f'{OLLAMA_HOST}/api/embeddings',
                json={'model': EMBED_MODEL, 'prompt': text},
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json().get('embedding')
        except Exception as e:
            print(f"[MEMORY] Embedding error: {e}")
        return None

    # ─── Short-Term Memory ───────────────────────────────

    def add_to_short_term(self, role: str, content: str):
        """Add an exchange to short-term memory."""
        self.short_term.append({'role': role, 'content': content})
        max_entries = self.max_short_term * 2  # user + assistant pairs
        if len(self.short_term) > max_entries:
            self.short_term = self.short_term[-max_entries:]

    def get_short_term_context(self) -> str:
        """Format short-term memory for prompt injection."""
        if not self.short_term:
            return ""
        lines = []
        for entry in self.short_term[-10:]:  # Last 5 exchanges
            role = "User" if entry['role'] == 'user' else "JARVIS"
            lines.append(f"{role}: {entry['content']}")
        return "Recent conversation:\n" + "\n".join(lines)

    # ─── Fact Memory (SQLite) ────────────────────────────

    def add_fact(self, category: str, key: str, value: str, confidence: float = 1.0):
        """Store or update a user fact."""
        if self.privacy_mode:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO facts (category, key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key) DO UPDATE SET
                    value = excluded.value,
                    confidence = excluded.confidence,
                    updated_at = CURRENT_TIMESTAMP
            ''', (category, key, value, confidence))
            conn.commit()
        print(f"[MEMORY] Fact stored: [{category}] {key} = {value}")

    def get_facts(self, category: str = None) -> List[Tuple]:
        """Retrieve stored facts."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute(
                    'SELECT category, key, value FROM facts WHERE category = ? ORDER BY updated_at DESC',
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT category, key, value FROM facts ORDER BY updated_at DESC'
                ).fetchall()
        return rows

    def delete_fact(self, key: str) -> bool:
        """Delete a specific fact."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM facts WHERE key LIKE ?', (f'%{key}%',))
            conn.commit()
            deleted = cursor.rowcount > 0
        return deleted

    # ─── Episode Memory (ChromaDB) ──────────────────────

    def add_episode(self, session_id: str, user_input: str, response: str, intent: str):
        """Store a conversation episode as a vector embedding."""
        if self.privacy_mode or not self.chroma_available:
            return

        doc = f"User: {user_input}\nJARVIS: {response}"
        embedding = self._embed(doc)
        if not embedding:
            return

        ts = datetime.now().isoformat()
        try:
            self.episodes.add(
                documents=[doc],
                embeddings=[embedding],
                metadatas=[{
                    'intent': intent,
                    'timestamp': ts,
                    'session_id': session_id,
                }],
                ids=[f'{session_id}_{ts}'],
            )
        except Exception as e:
            print(f"[MEMORY] ChromaDB add error: {e}")

    def search_episodes(self, query: str, n_results: int = None) -> List[str]:
        """Semantic search over past conversations."""
        if not self.chroma_available or self.episodes.count() == 0:
            return []

        n = min(n_results or MAX_SEMANTIC_RESULTS, self.episodes.count())
        embedding = self._embed(query)
        if not embedding:
            return []

        try:
            results = self.episodes.query(
                query_embeddings=[embedding],
                n_results=n,
            )
            if results and results['documents']:
                return results['documents'][0]
        except Exception as e:
            print(f"[MEMORY] ChromaDB search error: {e}")
        return []

    # ─── Conversation Log (SQLite) ──────────────────────

    def log_conversation(self, session_id: str, user_input: str,
                         response: str, intent: str, model_used: str = ''):
        """Log a conversation exchange to SQLite."""
        if self.privacy_mode:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO conversations (session_id, user_input, response, intent, model_used)
                   VALUES (?, ?, ?, ?, ?)''',
                (session_id, user_input, response, intent, model_used)
            )
            conn.commit()

    def get_recent_conversations(self, limit: int = 10) -> List[Tuple]:
        """Get recent conversation entries."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                'SELECT user_input, response, intent, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ).fetchall()
        return rows

    # ─── Pattern Memory ─────────────────────────────────

    def record_pattern(self, task_type: str):
        """Record a task execution for pattern detection."""
        if self.privacy_mode:
            return
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO patterns (task_type, hour_of_day, day_of_week, count, last_used)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(task_type, hour_of_day, day_of_week) DO UPDATE SET
                    count = count + 1,
                    last_used = CURRENT_TIMESTAMP
            ''', (task_type, now.hour, now.weekday()))
            conn.commit()

    def get_patterns(self, hour: int = None) -> List[Tuple]:
        """Get task patterns, optionally filtered by hour."""
        with sqlite3.connect(self.db_path) as conn:
            if hour is not None:
                rows = conn.execute(
                    '''SELECT task_type, count FROM patterns
                       WHERE hour_of_day BETWEEN ? AND ?
                       ORDER BY count DESC LIMIT 5''',
                    (hour - 1, hour + 1)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT task_type, SUM(count) as total FROM patterns GROUP BY task_type ORDER BY total DESC LIMIT 10'
                ).fetchall()
        return rows

    # ─── Full Context Builder ────────────────────────────

    def get_context(self, query: str) -> str:
        """
        Build a comprehensive context string from all memory layers.
        This is injected into every LLM prompt.
        """
        parts = []

        # 1. User facts (always include — this is the user profile)
        facts = self.get_facts()
        if facts:
            fact_lines = [f"  • {key}: {value}" for _, key, value in facts[:15]]
            parts.append("Known facts about user:\n" + "\n".join(fact_lines))

        # 2. Short-term context
        short_term = self.get_short_term_context()
        if short_term:
            parts.append(short_term)

        # 3. Semantic episode search (relevant past conversations)
        episodes = self.search_episodes(query)
        if episodes:
            parts.append(
                "Relevant past conversations:\n" +
                "\n---\n".join(episodes[:3])
            )

        return "\n\n".join(parts) if parts else ""

    # ─── LLM-Powered Fact Extraction ────────────────────

    def extract_facts_with_llm(self, user_input: str) -> List[Tuple[str, str, str]]:
        """
        Use the LLM to extract personal facts from user speech.
        Returns list of (category, key, value) tuples.
        """
        # Quick keyword check first — skip LLM for obvious non-facts
        fact_indicators = [
            'my name', 'i am', "i'm", 'i like', 'i hate', 'i prefer',
            'i work', 'i live', 'i study', 'remember that', 'my favorite',
            'my wife', 'my husband', 'my dog', 'my cat', 'my car',
            'i was born', 'my birthday', 'my age', 'my email', 'my phone',
            'i use', 'i need', 'call me',
        ]
        lower = user_input.lower()
        if not any(indicator in lower for indicator in fact_indicators):
            return []

        prompt = f"""Extract personal facts from this statement. 
If there are no personal facts, reply with "NONE".

Statement: "{user_input}"

Reply as JSON array: [{{"category": "personal|preference|work|location", "key": "short_key", "value": "the fact"}}]
Or reply: NONE"""

        try:
            resp = requests.post(
                f'{OLLAMA_HOST}/api/generate',
                json={'model': FAST_MODEL, 'prompt': prompt, 'stream': False},
                timeout=15,
            )
            result = resp.json().get('response', '').strip()

            if 'NONE' in result.upper():
                return []

            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                facts = json.loads(result[start:end])
                extracted = []
                for f in facts:
                    if isinstance(f, dict) and 'key' in f and 'value' in f:
                        cat = f.get('category', 'personal')
                        extracted.append((cat, f['key'], f['value']))
                return extracted
        except Exception as e:
            print(f"[MEMORY] Fact extraction error: {e}")

        return []

    # ─── Full Exchange Processing ────────────────────────

    def add_exchange(self, session_id: str, user_input: str,
                     response: str, intent: str, model_used: str = ''):
        """Process and store a full exchange across all memory layers."""
        # Short-term
        self.add_to_short_term('user', user_input)
        self.add_to_short_term('assistant', response)

        if self.privacy_mode:
            return

        # SQLite conversation log
        self.log_conversation(session_id, user_input, response, intent, model_used)

        # ChromaDB episode
        self.add_episode(session_id, user_input, response, intent)

        # Pattern tracking
        self.record_pattern(intent)

        # LLM fact extraction
        facts = self.extract_facts_with_llm(user_input)
        for category, key, value in facts:
            self.add_fact(category, key, value)

    # ─── Privacy & Management ────────────────────────────

    def set_privacy_mode(self, enabled: bool):
        """Toggle privacy mode."""
        self.privacy_mode = enabled
        status = "ON (no new memories stored)" if enabled else "OFF (normal operation)"
        print(f"[MEMORY] Privacy mode: {status}")

    def export_memories(self, filepath: str) -> str:
        """Export all memories to a JSON file."""
        with sqlite3.connect(self.db_path) as conn:
            data = {
                'exported_at': datetime.now().isoformat(),
                'facts': [
                    {'category': r[0], 'key': r[1], 'value': r[2]}
                    for r in conn.execute('SELECT category, key, value FROM facts').fetchall()
                ],
                'conversations': [
                    {
                        'session_id': r[0], 'user_input': r[1],
                        'response': r[2], 'intent': r[3], 'timestamp': r[4]
                    }
                    for r in conn.execute(
                        'SELECT session_id, user_input, response, intent, timestamp FROM conversations'
                    ).fetchall()
                ],
                'patterns': [
                    {'task_type': r[0], 'count': r[1]}
                    for r in conn.execute(
                        'SELECT task_type, SUM(count) FROM patterns GROUP BY task_type'
                    ).fetchall()
                ],
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return f"Exported {len(data['facts'])} facts, {len(data['conversations'])} conversations, {len(data['patterns'])} patterns to {filepath}"

    def wipe_memories(self, confirm: bool = False) -> str:
        """Wipe all memories. Requires explicit confirmation."""
        if not confirm:
            return "Memory wipe requires confirmation. Say 'wipe memory confirm' to proceed."

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM facts')
            conn.execute('DELETE FROM conversations')
            conn.execute('DELETE FROM patterns')
            conn.execute('DELETE FROM reminders')
            conn.commit()

        # Clear ChromaDB
        if self.chroma_available:
            try:
                import chromadb
                self.chroma.delete_collection('episodes')
                self.episodes = self.chroma.get_or_create_collection('episodes')
            except Exception:
                pass

        self.short_term.clear()
        return "All memories have been wiped. Starting fresh."

    def forget_about(self, topic: str) -> str:
        """Selectively forget facts and conversations about a topic."""
        with sqlite3.connect(self.db_path) as conn:
            facts_deleted = conn.execute(
                'DELETE FROM facts WHERE key LIKE ? OR value LIKE ?',
                (f'%{topic}%', f'%{topic}%')
            ).rowcount
            convos_deleted = conn.execute(
                'DELETE FROM conversations WHERE user_input LIKE ? OR response LIKE ?',
                (f'%{topic}%', f'%{topic}%')
            ).rowcount
            conn.commit()

        return f"Forgot {facts_deleted} facts and {convos_deleted} conversations about '{topic}'."

    def get_conversation_analytics(self) -> dict:
        """Analyze conversation history for insights."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
            by_intent = conn.execute(
                'SELECT intent, COUNT(*) as cnt FROM conversations GROUP BY intent ORDER BY cnt DESC'
            ).fetchall()
            by_hour = conn.execute(
                '''SELECT CAST(strftime('%H', timestamp) AS INT) as hour, COUNT(*) as cnt
                   FROM conversations GROUP BY hour ORDER BY cnt DESC LIMIT 5'''
            ).fetchall()
            recent_sessions = conn.execute(
                'SELECT DISTINCT session_id FROM conversations ORDER BY timestamp DESC LIMIT 5'
            ).fetchall()

        return {
            'total_conversations': total,
            'by_intent': {row[0]: row[1] for row in by_intent},
            'most_active_hours': {row[0]: row[1] for row in by_hour},
            'recent_sessions': len(recent_sessions),
        }
