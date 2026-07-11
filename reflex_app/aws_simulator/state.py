"""State management per AWS Simulator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, List, Any

import reflex as rx
from pydantic import BaseModel

from aws_simulator.config import DATA_DIR, EXAMS


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


class ExamState(rx.State):
    """State per selezione e caricamento esami."""
    
    available_exams: Dict[str, Dict] = {}
    selected_exam: Optional[str] = None
    exam_loaded: bool = False
    error_message: str = ""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carica lista esami disponibili
        self.available_exams = self._load_available_exams()
    
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
    questions: List[Question] = []
    current_question_index: int = 0
    selected_answer: Optional[str] = None
    
    # Risultati
    answers: Dict[int, str] = {}  # {question_number: selected_answer}
    correct_answers_count: int = 0
    
    # UI
    show_explanation: bool = False
    quiz_completed: bool = False
    is_loading: bool = False
    
    @rx.event(background=True)
    async def load_quiz(self, exam_id: str):
        """Carica le domande dall'esame selezionato."""
        async with self:
            self.is_loading = True
            self.exam_id = exam_id
            self.answers = {}
            self.selected_answer = None
            self.current_question_index = 0
            self.show_explanation = False
            self.quiz_completed = False
            self.correct_answers_count = 0
        
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
                    return [Question(**q) for q in questions_data]
            
            questions = await rx.run_in_thread(_load)
            print(f"✅ Domande caricate: {len(questions)}")
            
            async with self:
                self.questions = questions
                self.current_question_index = 0
                self.is_loading = False
        
        except Exception as e:
            print(f"❌ Errore nel caricamento: {e}")
            import traceback
            traceback.print_exc()
            async with self:
                self.is_loading = False
    
    @rx.event
    def select_answer(self, answer: str):
        """Seleziona una risposta."""
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
        
        self.show_explanation = True
    
    @rx.event
    def next_question(self):
        """Passa alla prossima domanda."""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.selected_answer = None
            self.show_explanation = False
        else:
            # Quiz completato
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
