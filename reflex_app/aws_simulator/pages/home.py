"""Pagina home con selezione esami."""
from __future__ import annotations

import reflex as rx
from aws_simulator.state import ExamState, QuizState
from aws_simulator.config import EXAMS, DATA_DIR
import json
from pathlib import Path


def _get_exam_question_count(exam_id: str) -> int:
    """Legge il numero di domande da JSON."""
    try:
        json_file = DATA_DIR / f"aws_{exam_id}.json"
        print(f"🔍 Home page cercando: {json_file}")
        if json_file.exists():
            print(f"✅ File trovato, leggo...")
            with open(json_file, "r") as f:
                data = json.load(f)
                count = data.get("total_questions", 0)
                print(f"✅ Domande trovate: {count}")
                return count
        else:
            print(f"❌ File non trovato: {json_file}")
    except Exception as e:
        print(f"❌ Errore lettura file: {e}")
    return 0


def exam_card(exam_id: str, exam_info: dict) -> rx.Component:
    """Card per singolo esame - Design moderno e sofisticato."""
    
    return rx.box(
        rx.vstack(
            # Immagine in alto - adattata per immagini verticali
            rx.box(
                rx.image(
                    src=exam_info["icon"],
                    width="100%",
                    height="auto",
                    max_height="18rem",
                    object_fit="contain",
                ),
                width="100%",
                height="auto",
                min_height="16rem",
                display="flex",
                align_items="center",
                justify_content="center",
                background="linear-gradient(135deg, rgba(255, 153, 0, 0.05) 0%, rgba(13, 110, 253, 0.05) 100%)",
                border_radius="lg lg 0 0",
                overflow="hidden",
                padding="1rem",
            ),
            
            # Contenuto card
            rx.vstack(
                # Header con badge livello
                rx.hstack(
                    rx.heading(
                        exam_info["code"],
                        size="5",
                        color="#0a1428",
                        font_weight="800",
                        letter_spacing="-0.5px",
                    ),
                    rx.spacer(),
                    rx.badge(
                        exam_info["level"],
                        color_scheme="orange",
                        size="2",
                        font_weight="600",
                    ),
                    width="100%",
                    align="center",
                ),
                
                # Nome esame
                rx.text(
                    exam_info["name"],
                    size="2",
                    color="#495057",
                    weight="medium",
                    line_height="1.4",
                ),
                
                # Specialità
                rx.box(
                    rx.hstack(
                        rx.box(width="3px", height="1rem", background="#FF9900", border_radius="2px"),
                        rx.text(
                            exam_info["speciality"],
                            size="1",
                            color="#FF9900",
                            weight="bold",
                            letter_spacing="0.5px",
                        ),
                        spacing="2",
                    ),
                ),
                
                # Descrizione
                rx.text(
                    exam_info["description"],
                    size="1",
                    color="#6c757d",
                    line_height="1.6",
                ),
                
                # Divider
                rx.divider(margin="1rem 0"),
                
                # Stats row
                rx.hstack(
                    rx.box(
                        rx.vstack(
                            rx.heading(
                                rx.cond(
                                    ExamState.available_exams.get(exam_id, {}).get("total_questions", 0) > 0,
                                    ExamState.available_exams.get(exam_id, {}).get("total_questions", "—"),
                                    "—",
                                ),
                                size="4",
                                color="#0d6efd",
                                font_weight="700",
                            ),
                            rx.text(
                                "Domande",
                                size="1",
                                color="#6c757d",
                                weight="medium",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        width="100%",
                    ),
                    rx.box(width="1px", height="2rem", background="#e9ecef"),
                    rx.box(
                        rx.vstack(
                            rx.heading(
                                f"{exam_info['duration']} min",
                                size="4",
                                color="#0d6efd",
                                font_weight="700",
                            ),
                            rx.text(
                                "Durata",
                                size="1",
                                color="#6c757d",
                                weight="medium",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                
                # Bottone CTA
                rx.button(
                    rx.hstack(
                        "Inizia Simulazione",
                        spacing="2",
                        width="100%",
                        justify_content="center",
                    ),
                    width="100%",
                    size="3",
                    color_scheme="blue",
                    font_weight="600",
                    on_click=[
                        ExamState.select_exam(exam_id),
                        QuizState.load_quiz(exam_id),
                        rx.redirect("/quiz"),
                    ],
                    _hover={
                        "transform": "translateY(-2px)",
                        "box_shadow": "0 12px 24px rgba(13, 110, 253, 0.25)",
                    },
                    transition="all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
                ),
                
                spacing="3",
                width="100%",
                padding="1.5rem",
            ),
            
            spacing="0",
            width="100%",
        ),
        width="100%",
        background="white",
        border_radius="lg",
        border="1px solid #e9ecef",
        box_shadow="0 4px 12px rgba(0, 0, 0, 0.08)",
        overflow="hidden",
        _hover={
            "box_shadow": "0 16px 32px rgba(0, 0, 0, 0.12)",
            "border_color": "#d9e1e8",
            "transition": "all 0.3s ease",
        },
        transition="all 0.3s ease",
    )


def exam_selection_grid() -> rx.Component:
    """Grid di selezione esami."""
    # Crea una lista di tuple (exam_id, exam_info_dict) per iterare
    exam_list = [(exam_id, exam_info) for exam_id, exam_info in EXAMS.items()]
    
    return rx.grid(
        rx.foreach(
            exam_list,
            lambda exam_tuple: exam_card(exam_tuple[0], exam_tuple[1]),
        ),
        columns=rx.cond(
            rx.breakpoints(initial="1", sm="1", md="2", lg="2", xl="2"),
            "2",
            "1",
        ),
        spacing="6",
        width="100%",
    )


@rx.page(route="/", title="AWS Exam Simulator")
def home_page() -> rx.Component:
    """Pagina principale - Design moderno e sofisticato."""
    return rx.vstack(
        # Top gradient bar
        rx.box(
            height="4px",
            background="linear-gradient(90deg, #FF9900 0%, #0d6efd 100%)",
        ),
        
        # Main content
        rx.vstack(
            # Hero section
            rx.vstack(
                rx.hstack(
                    # Logo/Icon
                    rx.box(
                        rx.image(
                            src="/favicon.ico",
                            height="3rem",
                            width="3rem",
                        ),
                        padding="0.75rem",
                        background="linear-gradient(135deg, rgba(255, 153, 0, 0.1) 0%, rgba(13, 110, 253, 0.1) 100%)",
                        border_radius="xl",
                    ),
                    
                    # Title
                    rx.vstack(
                        rx.heading(
                            "AWS Exam Simulator",
                            size="7",
                            color="#0a1428",
                            font_weight="800",
                            letter_spacing="-1px",
                        ),
                        rx.text(
                            "Pratica con gli esami di certificazione AWS ufficiali",
                            size="3",
                            color="#6c757d",
                            weight="medium",
                        ),
                        spacing="1",
                    ),
                    
                    align="start",
                    spacing="4",
                    width="100%",
                ),
                
                # Subtitle with stats
                rx.hstack(
                    rx.box(
                        rx.text(
                            "2",
                            size="4",
                            color="#FF9900",
                            weight="bold",
                        ),
                        rx.text(
                            "Esami Disponibili",
                            size="2",
                            color="#6c757d",
                        ),
                    ),
                    rx.box(width="1px", height="1.5rem", background="#e9ecef"),
                    rx.box(
                        rx.text(
                            f"{_get_exam_question_count('saa_c03') + _get_exam_question_count('aip_c01')}",
                            size="4",
                            color="#FF9900",
                            weight="bold",
                        ),
                        rx.text(
                            "Domande Totali",
                            size="2",
                            color="#6c757d",
                        ),
                    ),
                    rx.box(width="1px", height="1.5rem", background="#e9ecef"),
                    rx.box(
                        rx.text(
                            "∞",
                            size="4",
                            color="#FF9900",
                            weight="bold",
                        ),
                        rx.text(
                            "Simulazioni",
                            size="2",
                            color="#6c757d",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                
                spacing="6",
                width="100%",
            ),
            
            # Divider
            rx.divider(margin="2rem 0"),
            
            # Grid esami
            rx.vstack(
                rx.heading(
                    "Scegli il tuo esame",
                    size="4",
                    color="#0a1428",
                    font_weight="700",
                ),
                exam_selection_grid(),
                spacing="4",
                width="100%",
            ),
            
            # Footer
            rx.box(
                rx.text(
                    "© 2026 AWS Exam Simulator • Domande da ExamTopics • Progettato per l'eccellenza",
                    size="1",
                    color="#adb5bd",
                    text_align="center",
                ),
                width="100%",
                padding="2rem 0 1rem",
                border_top="1px solid #e9ecef",
            ),
            
            spacing="0",
            padding="3rem 2rem",
            width="100%",
            max_width="1400px",
            margin="0 auto",
        ),
        
        spacing="0",
        width="100%",
        min_height="100vh",
        background="linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)",
    )
