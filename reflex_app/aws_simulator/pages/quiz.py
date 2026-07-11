"""Pagina quiz con domande."""
from __future__ import annotations

import reflex as rx
from aws_simulator.state import QuizState, ExamState
from aws_simulator.config import EXAMS


def progress_bar() -> rx.Component:
    """Barra di progresso."""
    return rx.vstack(
        rx.hstack(
            rx.text(
                rx.cond(
                    QuizState.questions.length() > 0,
                    f"Domanda {QuizState.current_question_index + 1} di {QuizState.questions.length()}",
                    "Caricamento...",
                ),
                size="2",
                weight="medium",
                color="#495057",
            ),
            rx.spacer(),
            rx.text(
                rx.cond(
                    QuizState.questions.length() > 0,
                    rx.cond(
                        QuizState.progress_percentage >= 99,
                        "100%",
                        rx.cond(
                            QuizState.progress_percentage >= 75,
                            "75%",
                            rx.cond(
                                QuizState.progress_percentage >= 50,
                                "50%",
                                rx.cond(
                                    QuizState.progress_percentage >= 25,
                                    "25%",
                                    "0%",
                                ),
                            ),
                        ),
                    ),
                    "0%",
                ),
                size="2",
                weight="bold",
                color="#0d6efd",
            ),
            width="100%",
        ),
        # Usa un box colorato come barra alternativa
        rx.box(
            width="100%",
            height="8px",
            background=rx.cond(
                QuizState.progress_percentage >= 99,
                "linear-gradient(to right, #0d6efd 100%, #e9ecef 0%)",
                rx.cond(
                    QuizState.progress_percentage >= 75,
                    "linear-gradient(to right, #0d6efd 75%, #e9ecef 25%)",
                    rx.cond(
                        QuizState.progress_percentage >= 50,
                        "linear-gradient(to right, #0d6efd 50%, #e9ecef 50%)",
                        rx.cond(
                            QuizState.progress_percentage >= 25,
                            "linear-gradient(to right, #0d6efd 25%, #e9ecef 75%)",
                            "linear-gradient(to right, #0d6efd 0%, #e9ecef 100%)",
                        ),
                    ),
                ),
            ),
            border_radius="4px",
        ),
        spacing="2",
        width="100%",
    )


def question_card() -> rx.Component:
    """Card della domanda."""
    return rx.card(
        rx.vstack(
            # Numero topic
            rx.badge(
                f"Topic {QuizState.current_question.topic}",
                color_scheme="gray",
                size="1",
            ),
            
            # Testo domanda
            rx.heading(
                QuizState.current_question.text,
                size="4",
                color="#1e3a5f",
                font_weight="600",
                line_height="1.6",
            ),
            
            # Opzioni risposta
            rx.vstack(
                rx.foreach(
                    ["A", "B", "C", "D"],
                    lambda opt: rx.box(
                        rx.hstack(
                            # Pallino/cerchio personalizzato
                            rx.box(
                                rx.cond(
                                    QuizState.selected_answer == opt,
                                    rx.box(
                                        width="6px",
                                        height="6px",
                                        background="#0d6efd",
                                        border_radius="50%",
                                    ),
                                    rx.box(),
                                ),
                                width="20px",
                                height="20px",
                                border="2px solid #0d6efd",
                                border_radius="50%",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                flex_shrink="0",
                            ),
                            # Testo opzione
                            rx.text(
                                QuizState.current_question.options.get(opt, ""),
                                size="2",
                                line_height="1.6",
                                word_break="break-word",
                                white_space="normal",
                                overflow_wrap="break-word",
                            ),
                            width="100%",
                            spacing="3",
                            align="start",
                        ),
                        width="100%",
                        padding="3",
                        border=rx.cond(
                            QuizState.selected_answer == opt,
                            "2px solid #0d6efd",
                            "1px solid #e9ecef",
                        ),
                        border_radius="md",
                        background=rx.cond(
                            QuizState.selected_answer == opt,
                            "rgba(13, 110, 253, 0.05)",
                            "white",
                        ),
                        cursor="pointer",
                        transition="all 0.2s ease",
                        _hover={
                            "border_color": "#0d6efd",
                            "background": "rgba(13, 110, 253, 0.02)",
                        },
                        on_click=lambda: QuizState.select_answer(opt),
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            
            spacing="4",
            width="100%",
        ),
        size="4",
        width="100%",
    )


def explanation_section() -> rx.Component:
    """Sezione spiegazione risposta."""
    return rx.cond(
        QuizState.show_explanation,
        rx.card(
            rx.vstack(
                # Header risultato
                rx.hstack(
                    rx.cond(
                        QuizState.selected_answer == QuizState.current_question.correct_answer,
                        rx.text("✅ Risposta corretta!", weight="bold", color="#198754", size="3"),
                        rx.text("❌ Risposta errata", weight="bold", color="#dc3545", size="3"),
                    ),
                    rx.spacer(),
                    rx.text(
                        f"Risposta corretta: {QuizState.current_question.correct_answer}",
                        size="2",
                        color="#495057",
                        weight="medium",
                    ),
                    width="100%",
                ),
                
                rx.divider(),
                
                # Spiegazione
                rx.text(
                    QuizState.current_question.explanation,
                    size="2",
                    color="#495057",
                    line_height="1.6",
                ),
                
                spacing="3",
                width="100%",
            ),
            background="rgba(255, 153, 0, 0.05)",
            border_left="4px solid #FF9900",
            size="3",
            width="100%",
        ),
        rx.box(height="0"),
    )


def navigation_buttons() -> rx.Component:
    """Bottoni navigazione."""
    return rx.hstack(
        # Bottone indietro
        rx.button(
            "← Precedente",
            variant="outline",
            size="3",
            on_click=QuizState.previous_question(),
            is_disabled=QuizState.current_question_index <= 0,
        ),
        
        rx.spacer(),
        
        # Bottone invia/avanti
        rx.cond(
            QuizState.show_explanation,
            rx.button(
                "Avanti →",
                color_scheme="blue",
                size="3",
                on_click=QuizState.next_question(),
            ),
            rx.button(
                "Invia risposta",
                color_scheme="blue",
                size="3",
                on_click=QuizState.submit_answer(),
                is_disabled=QuizState.selected_answer == "",
            ),
        ),
        
        width="100%",
    )


def results_screen() -> rx.Component:
    """Schermata risultati."""
    return rx.vstack(
        rx.center(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        QuizState.score_percentage >= 70,
                        "Congratulazioni!",
                        "Quiz completato",
                    ),
                    size="7",
                    color="#1e3a5f",
                    text_align="center",
                ),
                
                rx.heading(
                    f"{QuizState.score_percentage:.0f}%",
                    size="6",
                    color="#0d6efd",
                    text_align="center",
                    font_weight="700",
                ),
                
                rx.text(
                    rx.cond(
                        QuizState.questions.length() > 0,
                        f"{QuizState.correct_answers_count} su {QuizState.questions.length()} domande corrette",
                        "Caricamento...",
                    ),
                    size="3",
                    color="#495057",
                    text_align="center",
                ),
                
                rx.divider(),
                
                rx.hstack(
                    rx.button(
                        "Ritorna alla Home",
                        size="3",
                        color_scheme="gray",
                        variant="outline",
                        on_click=rx.redirect("/"),
                    ),
                    rx.button(
                        "Ripeti Quiz",
                        size="3",
                        color_scheme="blue",
                        on_click=[
                            QuizState.reset_quiz(),
                        ],
                    ),
                    width="100%",
                    justify_content="center",
                ),
                
                spacing="4",
                align="center",
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
        justify_content="center",
        min_height="60vh",
    )


@rx.page(route="/quiz", title="Quiz – AWS Simulator")
def quiz_page() -> rx.Component:
    """Pagina quiz."""
    return rx.cond(
        QuizState.is_loading,
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Caricamento domande...", size="3", color="#6c757d"),
                spacing="3",
            ),
            width="100%",
            min_height="100vh",
        ),
        rx.cond(
            QuizState.quiz_completed,
            results_screen(),
            rx.vstack(
                # Header
                rx.hstack(
                    rx.button(
                        "✕",
                        variant="ghost",
                        on_click=rx.redirect("/"),
                        size="3",
                    ),
                    rx.spacer(),
                    rx.text(
                        ExamState.available_exams.get(
                            QuizState.exam_id,
                            {}
                        ).get("code", "Quiz"),
                        size="2",
                        weight="bold",
                        color="#495057",
                    ),
                    width="100%",
                    padding="3",
                    border_bottom="1px solid rgba(0, 0, 0, 0.1)",
                ),
                
                # Contenuto principale
                rx.vstack(
                    progress_bar(),
                    
                    # Debug info
                    rx.text(
                        rx.cond(
                            QuizState.questions.length() > 0,
                            f"DEBUG: {QuizState.questions.length()} domande caricate",
                            "DEBUG: Nessuna domanda caricata",
                        ),
                        size="1",
                        color="#adb5bd",
                    ),
                    
                    rx.cond(
                        QuizState.current_question,
                        rx.vstack(
                            question_card(),
                            explanation_section(),
                            navigation_buttons(),
                            spacing="4",
                            width="100%",
                        ),
                        rx.center(
                            rx.text(
                                "Nessuna domanda disponibile",
                                size="3",
                                color="#6c757d",
                            ),
                            width="100%",
                            min_height="400px",
                        ),
                    ),
                    
                    spacing="6",
                    padding="6",
                    width="100%",
                    max_width="900px",
                    margin_x="auto",
                ),
                
                spacing="0",
                width="100%",
            ),
        ),
    )
