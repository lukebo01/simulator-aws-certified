#!/usr/bin/env python3
"""
Script per generare spiegazioni in italiano delle risposte corrette.
Prende 4 domande alla volta e chiede a un LLM di spiegare perchè la risposta è corretta.

Usa BazaarLink API (base_url: https://bazaarlink.ai/api/v1)
Modello: anthropic/claude-haiku-4-5
API Key: sk-bl-UUlFT_sD3alq-caVnjz4oqsXUvYruPSHJ5M0H6K5uBey0Qzk
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time

# Per usare OpenAI SDK con BazaarLink
from openai import OpenAI

# Configurazione
BAZAARLINK_API_KEY = "sk-bl-UUlFT_sD3alq-caVnjz4oqsXUvYruPSHJ5M0H6K5uBey0Qzk"
BAZAARLINK_BASE_URL = "https://bazaarlink.ai/api/v1"
MODEL = "anthropic/claude-haiku-4-5"

# Inizializza client
client = OpenAI(
    base_url=BAZAARLINK_BASE_URL,
    api_key=BAZAARLINK_API_KEY,
)


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
    Manda 4 domande al LLM e riceve le spiegazioni in italiano.
    
    Args:
        questions: Lista di 4 domande
        
    Returns:
        Risposta del LLM con le spiegazioni
    """
    # Formatta tutte le domande
    formatted_questions = "\n\n---\n\n".join(
        format_question_for_llm(q) for q in questions
    )
    
    # Crea il prompt
    prompt = f"""Sei un esperto di certificazioni AWS. Per ognuna delle seguenti 4 domande, 
spiegami in italiano e in modo dettagliato perchè la risposta indicata è corretta, considerando:
- Lo scenario descritto nella domanda
- I dettagli tecnici di ogni opzione
- Perchè le altre opzioni sono sbagliate
- Principi AWS e best practices rilevanti

Rispondi in JSON con la seguente struttura, una voce per ogni domanda:
{{
  "question_number": <numero>,
  "correct_answer": "<lettera>",
  "explanation": "<spiegazione in italiano, 2-3 paragrafi>"
}}

Ecco le domande:

{formatted_questions}

Rispondi SOLO con un array JSON valido, niente altro."""

    print(f"🔄 Invio 4 domande al LLM...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    
    return response.choices[0].message.content


def parse_llm_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse la risposta JSON dal LLM."""
    try:
        # Estrai il JSON dalla risposta
        # Potrebbe contenere testo extra, quindi cerchiamo l'array JSON
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start == -1 or end == 0:
            print("❌ Errore: Nessun JSON trovato nella risposta")
            return []
        
        json_str = response_text[start:end]
        explanations = json.loads(json_str)
        
        return explanations
    except json.JSONDecodeError as e:
        print(f"❌ Errore nel parsing JSON: {e}")
        print(f"Risposta ricevuta: {response_text[:500]}")
        return []


def process_questions_in_batches(json_file: Path, output_file: Path = None, batch_size: int = 4):
    """
    Processa le domande in batch e salva le spiegazioni.
    
    Args:
        json_file: Path al file JSON con le domande
        output_file: Path al file di output (default: same name with _explained)
        batch_size: Numero di domande per batch (default: 4)
    """
    # Carica domande
    questions = load_questions(json_file)
    print(f"📚 Caricate {len(questions)} domande da {json_file.name}")
    
    # Setup output file
    if output_file is None:
        output_file = json_file.parent / f"{json_file.stem}_explained.json"
    
    # Inizializza struttura output
    all_explanations = {}
    
    # Processa in batch
    total_batches = (len(questions) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(questions))
        batch = questions[start_idx:end_idx]
        
        print(f"\n📋 Batch {batch_num + 1}/{total_batches} - Domande {start_idx + 1}-{end_idx}")
        
        # Chiedi al LLM
        response = get_explanation_from_llm(batch)
        
        # Parse risposta
        explanations = parse_llm_response(response)
        
        # Salva spiegazioni
        for explanation in explanations:
            if "question_number" in explanation:
                all_explanations[str(explanation["question_number"])] = explanation
                print(f"  ✅ Domanda #{explanation['question_number']}: Spiegazione ricevuta")
        
        # Rate limit: aspetta un po' tra i batch
        if batch_num < total_batches - 1:
            print("⏳ Aspetto 2 secondi prima del prossimo batch...")
            time.sleep(2)
    
    # Salva tutte le spiegazioni
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_explanations, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ Spiegazioni salvate in: {output_file}")
    print(f"📊 Totale spiegazioni: {len(all_explanations)}/{len(questions)}")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # File di input (puoi cambiar questo)
    json_file = project_root / "data" / "json_normalized" / "aws_saa_c03.json"
    
    if not json_file.exists():
        print(f"❌ File non trovato: {json_file}")
        sys.exit(1)
    
    print("🚀 Generatore di spiegazioni AWS Exam")
    print(f"📁 File: {json_file.name}")
    print(f"🔑 API: BazaarLink")
    print(f"🤖 Modello: {MODEL}\n")
    
    # Processa le domande
    process_questions_in_batches(json_file)
