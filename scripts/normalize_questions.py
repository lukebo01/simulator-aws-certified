#!/usr/bin/env python3
"""
Normalizzazione domande markdown in formato JSON interrogabile.

Converte i file markdown raw in JSON strutturato:
- aws_saa_c03.md → aws_saa_c03.json (AWS Solutions Architect Associate)
- aws_aip_c01.md → aws_aip_c01.json (AWS AI Practitioner)

Formato di output JSON:
{
  "exam": "AWS Certified Solutions Architect - Associate (SAA-C03)",
  "exam_code": "SAA-C03",
  "exam_type": "associate",
  "exam_specialty": "Solutions Architect",
  "total_questions": 342,
  "questions": [
    {
      "id": "saa-c03-001",
      "number": 239,
      "topic": 1,
      "text": "A solutions architect needs to design...",
      "options": {
        "A": "Create an Amazon API Gateway REST API...",
        "B": "Create a Lambda function URL...",
        "C": "Create an Amazon CloudFront distribution...",
        "D": "Create an Amazon CloudFront distribution..."
      },
      "correct_answer": "A",
      "explanation": "...",
      "source": "ExamTopics",
      "timestamp": "2023-01-15"
    }
  ]
}
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any


# Mappi di configurazione esami
EXAM_CONFIG = {
    "aws_saa_c03": {
        "exam": "AWS Certified Solutions Architect - Associate (SAA-C03)",
        "exam_code": "SAA-C03",
        "exam_type": "associate",
        "exam_specialty": "Solutions Architect",
        "display_name": "AWS Associate Solution Architect",
        "icon": "aws-saa.svg",
    },
    "aws_aip_c01": {
        "exam": "AWS Certified AI Practitioner (AIP-C01)",
        "exam_code": "AIP-C01",
        "exam_type": "professional",
        "exam_specialty": "Generative AI",
        "display_name": "AWS Generative AI Professional",
        "icon": "aws-aip.svg",
    },
}


def parse_exam_type(exam_type_str: str) -> Optional[str]:
    """Estrae il tipo di esame dal testo."""
    lower = exam_type_str.lower()
    if "solutions architect" in lower and "associate" in lower:
        return "aws_saa_c03"
    if "ai practitioner" in lower or "generative ai" in lower:
        return "aws_aip_c01"
    return None


def extract_question_number(text: str) -> Optional[int]:
    """Estrae il numero della domanda da testo come 'Question #: 239'."""
    match = re.search(r"Question\s*#\s*:\s*(\d+)", text)
    return int(match.group(1)) if match else None


def extract_topic_number(text: str) -> Optional[int]:
    """Estrae il numero del topic da testo come 'Topic #: 1'."""
    match = re.search(r"Topic\s*#\s*:\s*(\d+)", text)
    return int(match.group(1)) if match else None


def extract_timestamp(text: str) -> Optional[str]:
    """Estrae il timestamp nel formato ISO YYYY-MM-DD."""
    match = re.search(r"Timestamp:\s*(\w+)\.\s*(\d+),\s*(\d{4})", text)
    if match:
        month_str, day, year = match.groups()
        months = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
        }
        month = months.get(month_str.lower()[:3])
        if month:
            return f"{year}-{month}-{int(day):02d}"
    return None


def extract_answer(text: str) -> Optional[str]:
    """Estrae la risposta corretta da testo come '**Answer: A**'."""
    match = re.search(r"\*\*Answer\s*:\s*([A-D])\*\*", text)
    return match.group(1) if match else None


def parse_markdown_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parsa un file markdown e estrae le domande."""
    content = file_path.read_text(encoding="utf-8")
    
    # Dividi per sezioni di domande (iniziano con "## Exam")
    question_blocks = re.split(r"\n## Exam AWS", content)
    
    questions = []
    
    for idx, block in enumerate(question_blocks[1:], 1):  # Skip il primo split vuoto
        # Prepend la parte "## Exam AWS" per mantenere il formato
        block = "## Exam AWS" + block
        
        # Estrai i dati principali
        question_num = extract_question_number(block)
        topic_num = extract_topic_number(block)
        timestamp = extract_timestamp(block)
        answer = extract_answer(block)
        
        if not question_num or not answer:
            continue
        
        # Estratto il testo della domanda: cerca il pattern [All AWS...]
        # seguito da due newline, poi il testo fino alla prima opzione "\nA."
        question_match = re.search(
            r"\[All AWS[^\]]*\]\n\n(.+?)\n\nA\.",
            block,
            re.DOTALL
        )
        
        if not question_match:
            # Fallback: cerca il testo tra "Topic #:" e "\nA."
            question_match = re.search(
                r"Topic\s*#\s*:\s*\d+\n\n(.+?)\n\nA\.",
                block,
                re.DOTALL
            )
        
        question_text = question_match.group(1).strip() if question_match else "N/A"
        # Ripulisci il testo dalle newline extra - collassa spazi multipli
        question_text = re.sub(r'\s+', ' ', question_text).strip()
        
        # Estrai le opzioni A, B, C, D
        # Nel markdown ogni opzione è su una propria linea: "\nA. text\nB. text..."
        options = {}
        
        for opt in ["A", "B", "C", "D"]:
            next_opt = chr(ord(opt) + 1) if opt != "D" else None
            
            # Pattern: cattura da "\nX. " fino a "\nY. " (dove Y è la prossima lettera)
            # oppure fino a "\n**Answer" se è l'ultima
            if next_opt:
                # Cerca "\nX.\s+" fermandosi PRIMA di "\nY.\s+"
                pattern = rf"\n{opt}\.\s+(.+?)\n{next_opt}\."
            else:
                # Ultima opzione: fino a "\n**Answer"
                pattern = rf"\n{opt}\.\s+(.+?)\n\*\*Answer"
            
            match = re.search(pattern, block, re.DOTALL)
            if match:
                opt_text = match.group(1).strip()
                # Ripulisci: collassa whitespace multiplo
                opt_text = re.sub(r'\s+', ' ', opt_text).strip()
                options[opt] = opt_text



        
        # Estrai la spiegazione (dopo Answer fino a Link o fine)
        explanation_match = re.search(
            r"\*\*Answer:\s*[A-D]\*\*\s*\n\n(.+?)(?:\[View on ExamTopics\]|\n\n----|$)",
            block,
            re.DOTALL
        )
        explanation = (
            explanation_match.group(1).strip() 
            if explanation_match 
            else ""
        )
        # Ripulisci
        explanation = re.sub(r'\n+', ' ', explanation).strip()
        
        questions.append({
            "number": question_num,
            "topic": topic_num or 1,
            "text": question_text,
            "options": options,
            "correct_answer": answer,
            "explanation": explanation,
            "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d"),
        })
    
    return sorted(questions, key=lambda q: q["number"])


def normalize_questions(input_dir: Path, output_dir: Path):
    """Normalizza tutti i file markdown in JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for md_file in sorted(input_dir.glob("*.md")):
        # Determina il codice esame dal nome file
        stem = md_file.stem  # es. "aws_saa_c03"
        
        if stem not in EXAM_CONFIG:
            print(f"⚠️  {stem} non riconosciuto, skipping...")
            continue
        
        config = EXAM_CONFIG[stem]
        print(f"📖 Normalizzando {stem}...")
        
        # Parse markdown
        questions = parse_markdown_file(md_file)
        
        if not questions:
            print(f"  ❌ Nessuna domanda estratta da {md_file.name}")
            continue
        
        # Crea JSON output
        output_data = {
            "exam": config["exam"],
            "exam_code": config["exam_code"],
            "exam_type": config["exam_type"],
            "exam_specialty": config["exam_specialty"],
            "display_name": config["display_name"],
            "icon": config["icon"],
            "total_questions": len(questions),
            "last_updated": datetime.now().isoformat(),
            "questions": [
                {
                    "id": f"{stem}-{q['number']:03d}",
                    "number": q["number"],
                    "topic": q["topic"],
                    "text": q["text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "source": "ExamTopics",
                    "timestamp": q["timestamp"],
                }
                for q in questions
            ],
        }
        
        # Salva JSON
        output_file = output_dir / f"{stem}.json"
        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✅ Salvato: {output_file.name} ({len(questions)} domande)")


if __name__ == "__main__":
    import sys
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    raw_dir = project_root / "data" / "raw" / "from_examtopics"
    json_dir = project_root / "data" / "json_normalized"
    
    if not raw_dir.exists():
        print(f"❌ Directory non trovata: {raw_dir}")
        sys.exit(1)
    
    print(f"📁 Legge da: {raw_dir}")
    print(f"📁 Scrive in: {json_dir}")
    print()
    
    normalize_questions(raw_dir, json_dir)
    
    print()
    print("✨ Normalizzazione completata!")
