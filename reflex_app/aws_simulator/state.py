"""State management per AWS Simulator."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

import reflex as rx
from pydantic import BaseModel

from aws_simulator.config import DATA_DIR, EXAMS
from aws_simulator.database import get_db, UserProgress


class Question(BaseModel):
    """Modello per una domanda."""
    id: str
    number: int
    topic: int
    text: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    source: str
    timestamp: str


class QuizSession(BaseModel):
    """Modello per una sessione di quiz."""
    exam_id: str
    total_questions: int
    current_question_index: int
    answers: Dict[int, str] = {}  # {question_number: selected_answer}
    score: int = 0
    completed: bool = False


class UserState(rx.State):
    """State per gestione profili utenti."""
    
    current_user_id: Optional[str] = None
    current_user_name: str = ""
    all_profiles: List[Dict] = []
    
    def load_profiles(self):
        """Carica la lista di tutti i profili."""
        db = get_db()
        profiles = db.get_all_profiles()
        self.all_profiles = [
            {
                "id": p.id,
                "name": p.name,
                "created_at": p.created_at,
                "last_login": p.last_login,
            }
            for p in profiles
        ]
    
    @rx.event
    def create_new_profile(self, name: str):
        """Crea un nuovo profilo."""
        if not name or name.strip() == "":
            return
        
        db = get_db()
        profile = db.create_profile(name.strip())
        self.current_user_id = profile.id
        self.current_user_name = profile.name
        self.load_profiles()
    
    @rx.event
    def select_profile(self, user_id: str):
        """Seleziona un profilo."""
        db = get_db()
        db.update_last_login(user_id)
        
        profile = db.get_profile(user_id)
        if profile:
            self.current_user_id = user_id
            self.current_user_name = profile.name
    
    @rx.event
    def logout(self):
        """Logout."""
        self.current_user_id = None
        self.current_user_name = ""
    
    def check_profile_and_redirect(self):
        """Verifica se profilo è selezionato e redirige a /profiles se no."""
        if self.current_user_id is None or self.current_user_id == "":
            return rx.redirect("/profiles")


class ExamState(rx.State):
    """State per selezione e caricamento esami."""
    
    available_exams: Dict[str, Dict] = {}
    selected_exam: Optional[str] = None
    exam_loaded: bool = False
    error_message: str = ""
    
    @rx.event
    def load_exams(self):
        """Carica gli esami disponibili."""
        self.available_exams = self._load_available_exams()
        # Se solo un esame, selezionalo automaticamente
        if len(self.available_exams) == 1:
            self.selected_exam = list(self.available_exams.keys())[0]
    
    def _load_available_exams(self) -> Dict[str, Dict]:
        """Carica lista degli esami disponibili dai JSON."""
        print(f"📁 DATA_DIR: {DATA_DIR}")
        exams_meta = {}
        for exam_key, exam_info in EXAMS.items():
            # Converti il key da snake_case mantenendo gli underscores (saa_c03 → aws_saa_c03.json)
            json_file = DATA_DIR / f"aws_{exam_key}.json"
            print(f"🔍 Cercando {exam_key}: {json_file}")
            print(f"   Esiste: {json_file.exists()}")
            
            if json_file.exists():
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        exams_meta[exam_key] = {
                            **exam_info,
                            "total_questions": data.get("total_questions", 0),
                            "json_file": str(json_file),
                        }
                        print(f"✅ Caricato {exam_key}: {data.get('total_questions')} domande")
                except Exception as e:
                    print(f"❌ Errore caricamento {exam_key}: {e}")
        return exams_meta
    
    @rx.event
    @rx.event
    def select_exam(self, exam_id: str):
        """Seleziona un esame."""
        if exam_id in self.available_exams:
            self.selected_exam = exam_id
            self.exam_loaded = True
            self.error_message = ""
        else:
            self.error_message = f"Esame non trovato: {exam_id}"


class QuizState(rx.State):
    """State per la sessione di quiz."""
    
    # Dati sessione
    exam_id: str = ""
    mode: str = "practice"  # "practice" o "exam"
    questions: List[Question] = []
    current_question_index: int = 0
    selected_answer: Optional[str] = None
    
    # Risultati
    answers: Dict[int, str] = {}  # {question_number: selected_answer}
    correct_answers_count: int = 0
    
    # Timer (solo per exam mode)
    time_remaining_seconds: int = 0  # Tempo rimanente in secondi
    total_time_seconds: int = 0      # Tempo totale disponibile
    timer_active: bool = False       # Se il timer è in corso
    
    # UI
    show_explanation: bool = False
    quiz_completed: bool = False
    is_loading: bool = False
    time_expired: bool = False  # Se il tempo è scaduto
    
    @rx.event
    def start_quiz(self, exam_id: str, mode: str = "practice"):
        """Avvia il quiz salvando exam_id e mode, poi redirige."""
        print(f"🚀 START_QUIZ CHIAMATO: exam_id={exam_id}, mode={mode}")
        self.exam_id = exam_id
        self.mode = mode
        # Utilizza il riferimento alla classe QuizState per ottenere l'EventSpec corretto
        return [
            QuizState.load_quiz(exam_id, mode),
            rx.redirect("/quiz"),
        ]
    
    @rx.event(background=True)
    async def load_quiz(self, exam_id: str, mode: str = "practice"):
        """Carica le domande dall'esame selezionato."""
        async with self:
            self.is_loading = True
            self.exam_id = exam_id
            self.mode = mode
            self.answers = {}
            self.selected_answer = None
            self.current_question_index = 0
            self.show_explanation = False
            self.quiz_completed = False
            self.correct_answers_count = 0
            self.time_expired = False
            self.timer_active = False
        
        try:
            # Determina il file JSON - mantieni gli underscores (saa_c03 → aws_saa_c03.json)
            json_file = DATA_DIR / f"aws_{exam_id}.json"
            
            print(f"🔍 Cercando: {json_file}")
            print(f"📁 Esiste: {json_file.exists()}")
            
            if not json_file.exists():
                print(f"❌ File non trovato: {json_file}")
                async with self:
                    self.is_loading = False
                return
            
            # Carica domande
            def _load():
                print(f"📂 Aprendo file: {json_file}")
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    questions_data = data.get("questions", [])
                    print(f"📊 Domande trovate: {len(questions_data)}")
                    questions = [Question(**q) for q in questions_data]
                    
                    # In exam mode, seleziona un campione casuale di domande
                    if mode == "exam":
                        # Numero di domande per l'esame (normalmente 65)
                        num_questions = EXAMS.get(exam_id, {}).get("questions", 65)
                        if len(questions) > num_questions:
                            questions = random.sample(questions, num_questions)
                            print(f"🎲 Modalità exam: selezionate {len(questions)} domande casuali")
                        else:
                            print(f"⚠️  Domande disponibili ({len(questions)}) < richieste ({num_questions})")
                    
                    return questions
            
            questions = await rx.run_in_thread(_load)
            print(f"✅ Domande caricate: {len(questions)}")
            
            # Calcola tempo per l'esame (in minuti dal config)
            exam_info = EXAMS.get(exam_id, {})
            duration_minutes = exam_info.get("duration", 130)
            total_seconds = duration_minutes * 60
            
            # Se esercitazione, carica i progressi salvati
            loaded_progress = False
            if mode == "practice":
                try:
                    from aws_simulator.state import UserState
                    user_state = UserState()
                    if user_state.current_user_id:
                        from aws_simulator.database import get_db
                        db = get_db()
                        progress = db.get_progress(user_state.current_user_id, exam_id)
                        
                        if progress:
                            print(f"📚 Progresso caricato: {len(progress.completed_questions)} domande già fatte")
                            async with self:
                                self.questions = questions
                                self.answers = progress.completed_questions
                                self.correct_answers_count = progress.correct_count
                                self.current_question_index = min(progress.last_question_index, len(questions) - 1)
                                self.is_loading = False
                            loaded_progress = True
                except Exception as e:
                    print(f"⚠️  Errore caricamento progresso: {e}")
            
            if not loaded_progress:
                async with self:
                    self.questions = questions
                    self.current_question_index = 0
                    self.is_loading = False
                    self.total_time_seconds = total_seconds if mode == "exam" else 0
                    self.time_remaining_seconds = total_seconds if mode == "exam" else 0
                    
                    # Avvia il timer se in exam mode
                    if mode == "exam":
                        self.timer_active = True
                        print(f"⏱️  Timer avviato: {duration_minutes} minuti")
                
                # Esegui il yield per far partire il timer in background
                if mode == "exam":
                    yield QuizState.start_timer()
        
        except Exception as e:
            print(f"❌ Errore nel caricamento: {e}")
            import traceback
            traceback.print_exc()
            async with self:
                self.is_loading = False
    
    @rx.event(background=True)
    async def start_timer(self):
        """Avvia il timer che decrementa ogni secondo."""
        import asyncio
        
        while self.timer_active and self.time_remaining_seconds > 0:
            await asyncio.sleep(1)
            async with self:
                self.time_remaining_seconds -= 1
                if self.time_remaining_seconds <= 0:
                    self.time_expired = True
                    self.timer_active = False
                    self.quiz_completed = True
                    print("⏰ Tempo scaduto!")
            yield
    
    @rx.event
    def stop_timer(self):
        """Ferma il timer."""
        self.timer_active = False
    
    @rx.event
    def select_answer(self, answer: str):
        """Seleziona una risposta."""
        # In exam mode, non mostrare la spiegazione subito
        if self.mode == "exam":
            self.selected_answer = answer
            self.show_explanation = False
        else:
            # In practice mode, comportamento originale
            self.selected_answer = answer
            self.show_explanation = False
    
    @rx.event
    def submit_answer(self):
        """Invia la risposta e passa alla prossima domanda."""
        if not self.selected_answer or self.current_question_index >= len(self.questions):
            return
        
        question = self.questions[self.current_question_index]
        self.answers[question.number] = self.selected_answer
        
        # Verifica se corretta
        if self.selected_answer == question.correct_answer:
            self.correct_answers_count += 1
        
        # Mostra spiegazione solo in practice mode
        if self.mode == "practice":
            self.show_explanation = True
        else:
            # In exam mode, passa direttamente alla prossima domanda
            self.next_question()
    
    @rx.event
    def next_question(self):
        """Passa alla prossima domanda."""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.selected_answer = None
            self.show_explanation = False
        else:
            # Quiz completato
            self.timer_active = False
            self.quiz_completed = True
    
    @rx.event
    def previous_question(self):
        """Torna alla domanda precedente."""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            question_num = self.questions[self.current_question_index].number
            self.selected_answer = self.answers.get(question_num)
            self.show_explanation = False
    
    @rx.event
    def reset_quiz(self):
        """Resetta il quiz."""
        self.current_question_index = 0
        self.selected_answer = None
        self.answers = {}
        self.correct_answers_count = 0
        self.show_explanation = False
        self.quiz_completed = False
        self.timer_active = False
        self.time_expired = False
    
    @rx.event
    def save_results(self):
        """Salva i risultati dell'esame."""
        if not self.exam_id:
            return
        
        user_state = UserState()
        if not user_state.current_user_id:
            print("❌ Nessun utente selezionato")
            return
        
        db = get_db()
        score_percentage = self.score_percentage
        time_spent = max(0, self.total_time_seconds - self.time_remaining_seconds) if self.mode == "exam" else 0
        
        # Salva il risultato
        db.save_exam_result(
            user_id=user_state.current_user_id,
            exam_id=self.exam_id,
            score=score_percentage,
            correct=self.correct_answers_count,
            total=len(self.questions),
            mode=self.mode,
            time_spent=time_spent,
        )
        
        # Se è esercitazione, salva il progresso
        if self.mode == "practice":
            progress = UserProgress(
                exam_id=self.exam_id,
                completed_questions=self.answers,
                correct_count=self.correct_answers_count,
                last_question_index=self.current_question_index,
                last_updated=str(__import__("datetime").datetime.now().isoformat()),
                total_reviewed=len(self.questions),
            )
            db.save_progress(user_state.current_user_id, self.exam_id, progress)
    
    @rx.var
    def current_question(self) -> Optional[Question]:
        """Domanda corrente."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    @rx.var
    def progress_percentage(self) -> float:
        """Percentuale di progresso."""
        if not self.questions:
            return 0.0
        return (self.current_question_index + 1) / len(self.questions) * 100
    
    @rx.var
    def score_percentage(self) -> float:
        """Percentuale di punteggio."""
        if not self.questions:
            return 0.0
        return (self.correct_answers_count / len(self.questions)) * 100
    
    @rx.var
    def time_remaining_formatted(self) -> str:
        """Formatta il tempo rimanente (HH:MM:SS)."""
        hours = self.time_remaining_seconds // 3600
        minutes = (self.time_remaining_seconds % 3600) // 60
        seconds = self.time_remaining_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
