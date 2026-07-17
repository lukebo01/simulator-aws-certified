"""Pagina di selezione della modalità (Esercitazione vs Simulazione Esame)."""
from __future__ import annotations

from typing import Dict

import reflex as rx
from aws_simulator.state import QuizState, ExamState, UserState


def mode_card(
    title: str,
    emoji: str,
    description: str,
    details: list,
    color_scheme: str,
    mode: str,
) -> rx.Component:
    """Card per una modalità di quiz."""
    return rx.card(
        rx.vstack(
            # Emoji e titolo
            rx.heading(
                f"{emoji} {title}",
                size="5",
                color="#0a1428",
                font_weight="800",
                text_align="center",
            ),
            
            # Descrizione
            rx.text(
                description,
                size="2",
                color="#495057",
                text_align="center",
                line_height="1.6",
            ),
            
            rx.divider(),
            
            # Dettagli
            rx.vstack(
                rx.foreach(
                    details,
                    lambda detail: rx.hstack(
                        rx.box(
                            "✓",
                            color="#198754",
                            font_weight="bold",
                            width="1.5rem",
                            text_align="center",
                        ),
                        rx.text(
                            detail,
                            size="1",
                            color="#6c757d",
                        ),
                        width="100%",
                        spacing="2",
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            
            rx.spacer(),
            
            # Bottone CTA
            rx.button(
                f"Inizia {title}",
                width="100%",
                size="3",
                color_scheme=color_scheme,
                font_weight="600",
                on_click=lambda: QuizState.start_quiz(ExamState.selected_exam, mode),
                _hover={
                    "transform": "translateY(-2px)",
                    "box_shadow": f"0 12px 24px rgba(0, 0, 0, 0.15)",
                },
                transition="all 0.3s ease",
            ),
            
            spacing="4",
            width="100%",
            padding="2rem",
        ),
        width="100%",
        background="white",
        border_radius="lg",
        border="1px solid #e9ecef",
        box_shadow="0 4px 12px rgba(0, 0, 0, 0.08)",
        _hover={
            "box_shadow": "0 16px 32px rgba(0, 0, 0, 0.12)",
            "border_color": "#d9e1e8",
            "transition": "all 0.3s ease",
        },
        transition="all 0.3s ease",
    )


def exam_card_component(exam_id: str) -> rx.Component:
    """Card per la selezione di un esame - usa solo exam_id come reactive var."""
    return rx.card(
        rx.vstack(
            rx.heading(
                exam_id.upper(),
                size="4",
                color="#0a1428",
                font_weight="700",
                text_align="center",
            ),
            rx.text(
                "Esame certificazione AWS",
                size="2",
                color="#6c757d",
                text_align="center",
            ),
            rx.divider(),
            rx.button(
                "✓ Seleziona questo esame",
                width="100%",
                size="3",
                color_scheme=rx.cond(
                    ExamState.selected_exam == exam_id,
                    "blue",
                    "gray",
                ),
                variant=rx.cond(
                    ExamState.selected_exam == exam_id,
                    "solid",
                    "outline",
                ),
                on_click=ExamState.select_exam(exam_id),
                font_weight="600",
            ),
            spacing="3",
            width="100%",
            padding="2rem 1rem",
        ),
        width="100%",
        background=rx.cond(
            ExamState.selected_exam == exam_id,
            "#dbeafe",
            "white",
        ),
        border_radius="lg",
        border=rx.cond(
            ExamState.selected_exam == exam_id,
            "2px solid #0d6efd",
            "1px solid #e9ecef",
        ),
        cursor="pointer",
    )


def exam_card(exam_id: str, exam_info: Dict) -> rx.Component:
    """Card per la selezione di un esame."""
    return rx.card(
        rx.vstack(
            rx.heading(
                exam_info.get("code", exam_id),
                size="4",
                color="#0a1428",
                font_weight="700",
                text_align="center",
            ),
            rx.text(
                exam_info.get("name", ""),
                size="1",
                color="#6c757d",
                text_align="center",
            ),
            rx.divider(),
            rx.hstack(
                rx.text(
                    "📝",
                    size="3",
                ),
                rx.vstack(
                    rx.text(
                        f"{exam_info.get('total_questions', 0)} domande",
                        size="2",
                        weight="bold",
                        color="#0a1428",
                    ),
                    spacing="0",
                ),
                width="100%",
                spacing="2",
                align="center",
            ),
            rx.button(
                "Seleziona",
                width="100%",
                size="2",
                color_scheme=rx.cond(
                    ExamState.selected_exam == exam_id,
                    "blue",
                    "gray",
                ),
                variant=rx.cond(
                    ExamState.selected_exam == exam_id,
                    "solid",
                    "outline",
                ),
                on_click=ExamState.select_exam(exam_id),
            ),
            spacing="3",
            width="100%",
            padding="1.5rem",
        ),
        width="100%",
        background=rx.cond(
            ExamState.selected_exam == exam_id,
            "#e7f5ff",
            "white",
        ),
        border_radius="md",
        border=rx.cond(
            ExamState.selected_exam == exam_id,
            "2px solid #0d6efd",
            "1px solid #e9ecef",
        ),
        box_shadow=rx.cond(
            ExamState.selected_exam == exam_id,
            "0 4px 12px rgba(13, 110, 253, 0.15)",
            "0 2px 8px rgba(0, 0, 0, 0.08)",
        ),
        cursor="pointer",
        _hover={
            "box_shadow": "0 8px 16px rgba(0, 0, 0, 0.12)",
            "transition": "all 0.3s ease",
        },
        transition="all 0.3s ease",
    )


@rx.page(route="/mode-selection", title="Selezione Modalità – AWS Simulator", on_load=ExamState.load_exams)
def mode_selection_page() -> rx.Component:
    """Pagina di selezione della modalità."""
    return rx.vstack(
        # Top gradient bar
        rx.box(
            height="4px",
            background="linear-gradient(90deg, #FF9900 0%, #0d6efd 100%)",
        ),
        
        # Main content
        rx.vstack(
            # Header con profilo
            rx.hstack(
                rx.button(
                    "← Indietro",
                    variant="ghost",
                    on_click=rx.redirect("/profiles"),
                    size="2",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.text(
                        "👤 " + UserState.current_user_name,
                        size="2",
                        weight="bold",
                        color="#495057",
                    ),
                    rx.button(
                        "Logout",
                        size="1",
                        color_scheme="red",
                        variant="outline",
                        on_click=[
                            UserState.logout(),
                            rx.redirect("/"),
                        ],
                    ),
                    spacing="2",
                ),
                width="100%",
                padding="2rem",
                border_bottom="1px solid rgba(0, 0, 0, 0.1)",
                align="center",
            ),
            
            # Contenuto
            rx.vstack(
                rx.text(
                    "Scegli come vuoi allenarti per l'esame",
                    size="3",
                    color="#6c757d",
                    text_align="center",
                    margin_bottom="2rem",
                ),
                
                # Grid di modalità
                rx.grid(
                    # Esercitazione
                    mode_card(
                        title="Esercitazione",
                        emoji="📖",
                        description="Pratica con tutte le domande disponibili",
                        details=[
                            "Tutte le domande dell'esame",
                            "Vedi la risposta corretta subito",
                            "Leggi la spiegazione dopo ogni domanda",
                            "Nessun limite di tempo",
                            "Salva il tuo progresso automaticamente",
                        ],
                        color_scheme="blue",
                        mode="practice",
                    ),
                    
                    # Simulazione Esame
                    mode_card(
                        title="Simulazione Esame",
                        emoji="🎯",
                        description="Prova reale con timer e domande casuali",
                        details=[
                            "65 domande casuali",
                            "Tempo limitato (130-180 min)",
                            "Le risposte corrette si vedono alla fine",
                            "Simulazione realistica",
                            "Risultato salvato in classifica",
                        ],
                        color_scheme="orange",
                        mode="exam",
                    ),
                    
                    columns=rx.cond(
                        rx.breakpoints(initial="1", sm="1", md="2", lg="2", xl="2"),
                        "2",
                        "1",
                    ),
                    spacing="6",
                    width="100%",
                ),
                
                spacing="6",
                padding="2rem 1rem",
                width="100%",
                max_width="1000px",
                margin_x="auto",
            ),
            
            spacing="0",
            width="100%",
            min_height="100vh",
            background="linear-gradient(135deg, #f8f9fa 0%, #e8f0fe 100%)",
            on_mount=ExamState.load_exams,
        ),
        
        spacing="0",
        width="100%",
    )
