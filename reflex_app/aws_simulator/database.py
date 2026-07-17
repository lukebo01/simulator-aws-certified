"""Gestione database per profili utenti e progressi."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class UserProgress(BaseModel):
    """Progresso di un utente su un esame in modalità esercitazione."""
    exam_id: str
    completed_questions: Dict[int, str] = {}  # {question_number: answer}
    correct_count: int = 0
    last_question_index: int = 0
    last_updated: str = ""
    total_reviewed: int = 0


class UserProfile(BaseModel):
    """Profilo di un utente."""
    id: str
    name: str
    created_at: str
    last_login: str
    progress: Dict[str, UserProgress] = {}  # {exam_id: UserProgress}
    exam_results: Dict[str, Dict] = {}  # {exam_id: {score, date, mode, etc}}


class Database:
    """Gestione database JSON per profili utenti."""
    
    def __init__(self):
        self.db_path = Path(__file__).parent / "data" / "profiles.json"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Crea il file database se non esiste."""
        if not self.db_path.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict:
        """Carica i dati dal database."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento database: {e}")
            return {}
    
    def _save_data(self, data: Dict):
        """Salva i dati nel database."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Errore salvataggio database: {e}")
    
    def create_profile(self, name: str) -> UserProfile:
        """Crea un nuovo profilo utente."""
        data = self._load_data()
        
        # Genera ID univoco
        user_id = f"user_{len(data) + 1}_{int(datetime.now().timestamp())}"
        
        now = datetime.now().isoformat()
        profile = UserProfile(
            id=user_id,
            name=name,
            created_at=now,
            last_login=now,
        )
        
        data[user_id] = profile.model_dump()
        self._save_data(data)
        
        print(f"✅ Profilo creato: {name} (ID: {user_id})")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Recupera un profilo utente."""
        data = self._load_data()
        if user_id in data:
            return UserProfile(**data[user_id])
        return None
    
    def get_all_profiles(self) -> List[UserProfile]:
        """Recupera tutti i profili."""
        data = self._load_data()
        return [UserProfile(**profile_data) for profile_data in data.values()]
    
    def update_last_login(self, user_id: str):
        """Aggiorna il timestamp dell'ultimo login."""
        data = self._load_data()
        if user_id in data:
            data[user_id]["last_login"] = datetime.now().isoformat()
            self._save_data(data)
    
    def save_progress(self, user_id: str, exam_id: str, progress: UserProgress):
        """Salva il progresso di esercitazione per un utente."""
        data = self._load_data()
        if user_id in data:
            data[user_id]["progress"][exam_id] = progress.model_dump()
            self._save_data(data)
            print(f"✅ Progresso salvato per {user_id} - {exam_id}")
    
    def get_progress(self, user_id: str, exam_id: str) -> Optional[UserProgress]:
        """Recupera il progresso di esercitazione."""
        data = self._load_data()
        if user_id in data and exam_id in data[user_id]["progress"]:
            return UserProgress(**data[user_id]["progress"][exam_id])
        return None
    
    def save_exam_result(
        self,
        user_id: str,
        exam_id: str,
        score: float,
        correct: int,
        total: int,
        mode: str,
        time_spent: int = 0,
    ):
        """Salva il risultato di un esame (simulazione)."""
        data = self._load_data()
        if user_id in data:
            result = {
                "score": score,
                "correct": correct,
                "total": total,
                "mode": mode,
                "date": datetime.now().isoformat(),
                "time_spent": time_spent,
            }
            if "exam_results" not in data[user_id]:
                data[user_id]["exam_results"] = {}
            
            # Salva come lista di risultati per lo stesso esame
            if exam_id not in data[user_id]["exam_results"]:
                data[user_id]["exam_results"][exam_id] = []
            
            data[user_id]["exam_results"][exam_id].append(result)
            self._save_data(data)
            print(f"✅ Risultato salvato: {user_id} - {exam_id} - Score: {score}%")
    
    def get_leaderboard(self, exam_id: str, mode: str = "exam") -> List[Dict]:
        """Recupera la classifica per un esame (top 10)."""
        data = self._load_data()
        scores = []
        
        for user_id, profile_data in data.items():
            name = profile_data.get("name", "Unknown")
            
            if "exam_results" in profile_data and exam_id in profile_data["exam_results"]:
                results = profile_data["exam_results"][exam_id]
                
                # Filtra per modalità se specificato
                if mode:
                    results = [r for r in results if r.get("mode") == mode]
                
                # Prendi il miglior risultato
                if results:
                    best = max(results, key=lambda x: x["score"])
                    scores.append({
                        "user_id": user_id,
                        "name": name,
                        "score": best["score"],
                        "correct": best["correct"],
                        "total": best["total"],
                        "date": best["date"],
                        "mode": best.get("mode", "exam"),
                    })
        
        # Ordina per score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:10]  # Top 10
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Recupera statistiche complessive di un utente."""
        profile = self.get_profile(user_id)
        if not profile:
            return {}
        
        stats = {
            "name": profile.name,
            "created_at": profile.created_at,
            "total_exams_taken": 0,
            "average_score": 0.0,
            "exams": {},
        }
        
        total_score = 0
        count = 0
        
        for exam_id, results in profile.exam_results.items():
            exam_stats = {
                "attempts": len(results),
                "best_score": max(r["score"] for r in results),
                "average": sum(r["score"] for r in results) / len(results),
                "results": results,
            }
            stats["exams"][exam_id] = exam_stats
            total_score += exam_stats["best_score"]
            count += 1
        
        stats["total_exams_taken"] = count
        stats["average_score"] = total_score / count if count > 0 else 0.0
        
        return stats


# Singleton
_db = None

def get_db() -> Database:
    """Ritorna l'istanza del database."""
    global _db
    if _db is None:
        _db = Database()
    return _db
