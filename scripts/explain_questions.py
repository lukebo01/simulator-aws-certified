#!/usr/bin/env python3
"""
Script per generare spiegazioni in italiano e aggiornare i JSON.
Prende 5 domande alla volta, chiede al LLM e aggiorna direttamente i file normalizzati.

Con CHECKPOINT di progresso - riprende da dove era rimasto se fallisce!

Usa Google Gemini API REST (GRATIS!)
Modello: gemini-3.5-flash (veloce e affidabile)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time
import requests

# Configurazione
#lukeman.stark@gmail.com
#GEMINI_API_KEY = "${GEMINI_API_KEY}"

#lucaborrelli.work@gmail.com
GEMINI_API_KEY = "${GEMINI_API_KEY}"

#ciccinideromatre@gmail.com
#GEMINI_API_KEY = "${GEMINI_API_KEY}"

#lucaborrelli.filo@gmail.com
#GEMINI_API_KEY = "${GEMINI_API_KEY}"

MODEL = "gemini-3.5-flash"  # Veloce e affidabile
BATCH_SIZE = 5  # 5 domande per batch
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def get_checkpoint_file(json_file: Path) -> Path:
    """Ritorna il path del file di checkpoint."""
    return json_file.parent / f".{json_file.stem}_checkpoint.json"


def load_checkpoint(json_file: Path) -> Dict[str, Any]:
    """Carica il checkpoint di progresso."""
    checkpoint_file = get_checkpoint_file(json_file)
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            return json.load(f)
    return {"last_batch": -1, "total_updated": 0, "failed_batches": []}


def save_checkpoint(json_file: Path, batch_num: int, total_updated: int, failed_batches: List[int]):
    """Salva il checkpoint di progresso."""
    checkpoint_file = get_checkpoint_file(json_file)
    checkpoint = {
        "last_batch": batch_num,
        "total_updated": total_updated,
        "failed_batches": failed_batches,
        "timestamp": time.time()
    }
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint, f)


def load_questions(json_file: Path) -> List[Dict[str, Any]]:
    """Carica le domande dal file JSON."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def format_question_for_llm(question: Dict[str, Any]) -> str:
    """Formatta una domanda per mandarla al LLM."""
    text = f"""Domanda #{question['number']} - Topic {question['topic']}

{question['text']}

A) {question['options']['A']}
B) {question['options']['B']}
C) {question['options']['C']}
D) {question['options']['D']}

Risposta corretta: {question['correct_answer']}
"""
    return text


def get_explanation_from_llm(questions: List[Dict[str, Any]]) -> str:
    """
    Manda 5 domande al LLM via REST API e riceve spiegazioni in italiano come JSON.
    Usa gemini-3.5-flash per velocità, fallback a gemini-2.0-flash se non disponibile.
    """
    formatted_questions = "\n\n---\n\n".join(
        format_question_for_llm(q) for q in questions
    )
    
    prompt = f"""Sei un esperto di certificazioni AWS. Per ognuna delle seguenti {len(questions)} domande,
spiegami in italiano e in modo dettagliato perchè la risposta indicata è corretta, considerando:
- Lo scenario descritto nella domanda
- I dettagli tecnici di ogni opzione
- Perchè le altre opzioni sono sbagliate
- Principi AWS e best practices rilevanti

Rispondi SOLO con un JSON valido in questo esatto formato (niente altro, solo JSON):
[
  {{
    "number": <numero domanda>,
    "correct_answer": "<lettera>",
    "explanation": "<spiegazione in italiano, 2-3 paragrafi>"
  }}
]

Ecco le domande:

{formatted_questions}"""

    print(f"🔄 Invio {len(questions)} domande a Gemini...")
    
    # Prova modelli in ordine di preferenza
    models_to_try = ["gemini-3.5-flash"]
    
    for model in models_to_try:
        try:
            url = f"{API_BASE_URL}/{model}:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            print(f"   Tentando con {model}...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if "candidates" in data and len(data["candidates"]) > 0:
                print(f"   ✓ {model} OK")
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"   ⚠️  Risposta vuota da {model}")
                continue
        
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "503" in error_msg or "UNAVAILABLE" in error_msg:
                print(f"   ⚠️  {model} sovraccarico, provo il prossimo...")
                continue
            else:
                print(f"   ❌ Errore con {model}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"      Status: {e.response.status_code}")
                continue
    
    # Se tutti i modelli falliscono
    raise Exception("Nessun modello disponibile - riprova più tardi")


def parse_llm_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse la risposta JSON dal LLM."""
    try:
        # Estrai il JSON dalla risposta
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start == -1 or end == 0:
            print(f"❌ Nessun JSON trovato nella risposta")
            return []
        
        json_str = response_text[start:end]
        
        try:
            explanations = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalido: {e}")
            print(f"   Tentativo JSON (primi 200 char): {json_str[:200]}")
            return []
        
        # Valida struttura
        valid_explanations = []
        for exp in explanations:
            if not isinstance(exp, dict):
                print(f"   ⚠️  Elemento non è dict: {type(exp)}")
                continue
            if "number" not in exp or "explanation" not in exp:
                print(f"   ⚠️  Elemento manca di campi obbligatori: {exp}")
                continue
            valid_explanations.append(exp)
        
        if not valid_explanations and explanations:
            print(f"❌ Nessuna spiegazione valida nel JSON")
        
        return valid_explanations
    
    except Exception as e:
        print(f"❌ Errore parsing: {e}")
        return []


def update_json_file(json_file: Path, explanations: List[Dict[str, Any]]):
    """Aggiorna il file JSON con le nuove spiegazioni."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Crea una mappa per accesso veloce
        exp_map = {exp["number"]: exp["explanation"] for exp in explanations}
        
        # Aggiorna le domande
        updated_count = 0
        for question in data["questions"]:
            if question["number"] in exp_map:
                question["explanation"] = exp_map[question["number"]]
                updated_count += 1
        
        # Salva il file aggiornato
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return updated_count
    
    except KeyError as e:
        print(f"❌ KeyError durante aggiornamento: {e}")
        print(f"   Spiegazioni ricevute: {explanations}")
        raise
    except Exception as e:
        print(f"❌ Errore durante aggiornamento: {e}")
        raise


def process_questions_in_batches(json_file: Path, batch_size: int = BATCH_SIZE):
    """
    Processa le domande in batch e aggiorna il JSON direttamente.
    Usa checkpoint per riprendere da dove era rimasto.
    """
    questions = load_questions(json_file)
    print(f"📚 Caricate {len(questions)} domande da {json_file.name}")
    
    total_batches = (len(questions) + batch_size - 1) // batch_size
    
    # Carica checkpoint
    checkpoint = load_checkpoint(json_file)
    last_batch = checkpoint["last_batch"]
    total_updated = checkpoint["total_updated"]
    failed_batches = checkpoint["failed_batches"]
    
    if last_batch >= 0:
        print(f"📌 Checkpoint trovato!")
        print(f"   ✅ Ultimo batch riuscito: {last_batch}/{total_batches - 1}")
        print(f"   📊 Domande aggiornate finora: {total_updated}")
        if failed_batches:
            print(f"   ⚠️  Batch falliti: {failed_batches}")
        print(f"   🔄 Riprendo da batch {last_batch + 1}...\n")
        start_batch = last_batch + 1
    else:
        print(f"🆕 Nessun checkpoint trovato - inizio da zero\n")
        start_batch = 0
    
    for batch_num in range(start_batch, total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(questions))
        batch = questions[start_idx:end_idx]
        
        print(f"📋 Batch {batch_num + 1}/{total_batches} - Domande {start_idx + 1}-{end_idx}")
        
        try:
            # Chiedi al LLM
            response = get_explanation_from_llm(batch)
            
            # Parse risposta
            explanations = parse_llm_response(response)
            
            if explanations:
                # Aggiorna il JSON
                updated = update_json_file(json_file, explanations)
                total_updated += updated
                print(f"  ✅ Aggiornate {updated} domande")
                
                # Salva checkpoint di successo
                save_checkpoint(json_file, batch_num, total_updated, failed_batches)
            else:
                print(f"  ⚠️  Nessuna spiegazione valida - salto questo batch")
                failed_batches.append(batch_num)
                save_checkpoint(json_file, batch_num - 1 if batch_num > 0 else -1, total_updated, failed_batches)
        
        except Exception as e:
            print(f"  ❌ ERRORE: {e}")
            failed_batches.append(batch_num)
            save_checkpoint(json_file, batch_num - 1 if batch_num > 0 else -1, total_updated, failed_batches)
            print(f"  💾 Checkpoint salvato - riprendi con lo stesso comando\n")
            return  # Esce per permettere di riavviare
        
        # Rate limit: aspetta tra i batch
        if batch_num < total_batches - 1:
            print("⏳ Aspetto 2 secondi...")
            time.sleep(2)
    
    print(f"\n✨ Aggiornamento COMPLETATO!")
    print(f"📊 Totale aggiornate: {total_updated}/{len(questions)}")
    if failed_batches:
        print(f"⚠️  Batch falliti: {set(failed_batches)} - riprova questi batch manualmente")
    
    # Rimuovi checkpoint al completamento se tutti i batch sono stati elaborati
    checkpoint_file = get_checkpoint_file(json_file)
    if checkpoint_file.exists() and len(failed_batches) < total_batches:
        checkpoint_file.unlink()
        print("🗑️  Checkpoint rimosso")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # File di input
    json_file = project_root / "data" / "json_normalized" / "aws_saa_c03.json"
    
    if not json_file.exists():
        print(f"❌ File non trovato: {json_file}")
        sys.exit(1)
    
    print("🚀 Generatore di spiegazioni AWS Exam")
    print(f"📁 File: {json_file.name}")
    print(f"🔑 API: Google Gemini REST (GRATIS)")
    print(f"🤖 Modelli: gemini-2.0-flash → gemini-3.5-flash (fallback)")
    print(f"📦 Batch size: {BATCH_SIZE} domande")
    print(f"💾 Con CHECKPOINT di progresso")
    print(f"⏳ Se carico alto: aspetta e riprova\n")
    
    process_questions_in_batches(json_file, BATCH_SIZE)
