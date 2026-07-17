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
    """Sezione spiegazione risposta (solo practice mode)."""
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
        
        # Comportamento diverso per practice vs exam mode
        rx.cond(
            QuizState.mode == "practice",
            # PRACTICE MODE: mostra spiegazione dopo submit
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
            # EXAM MODE: passa direttamente alla prossima domanda
            rx.button(
                rx.cond(
                    QuizState.current_question_index >= QuizState.questions.length() - 1,
                    "Completa Esame",
                    "Avanti →",
                ),
                color_scheme="orange",
                size="3",
                on_click=QuizState.submit_answer(),
                is_disabled=QuizState.selected_answer == "",
            ),
        ),
        
        width="100%",
    )


def results_screen() -> rx.Component:
    """Schermata risultati finali."""
    return rx.vstack(
        rx.center(
            rx.vstack(
                # Messaggio di risultato
                rx.heading(
                    rx.cond(
                        QuizState.time_expired,
                        "⏰ Tempo scaduto!",
                        rx.cond(
                            QuizState.score_percentage >= 720,  # Passing score per SAA-C03
                            "✅ Sei idoneo!",
                            rx.cond(
                                QuizState.score_percentage >= 70,
                                "🎉 Congratulazioni!",
                                "Quiz completato",
                            ),
                        ),
                    ),
                    size="7",
                    color="#1e3a5f",
                    text_align="center",
                ),
                
                # Score
                rx.heading(
                    f"{QuizState.score_percentage:.0f}%",
                    size="6",
                    color=rx.cond(
                        QuizState.score_percentage >= 70,
                        "#198754",  # Verde
                        "#dc3545",  # Rosso
                    ),
                    text_align="center",
                    font_weight="700",
                ),
                
                # Dettagli
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
                
                # Per exam mode, mostra tutte le risposte e spiegazioni
                rx.cond(
                    QuizState.mode == "exam",
                    rx.vstack(
                        rx.divider(),
                        rx.heading(
                            "Riepilogo risposte",
                            size="5",
                            color="#1e3a5f",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.foreach(
                                    QuizState.questions,
                                    lambda q: rx.card(
                                        rx.vstack(
                                            # Domanda
                                            rx.heading(
                                                f"Domanda {q.number}",
                                                size="3",
                                                color="#1e3a5f",
                                            ),
                                            rx.text(q.text, size="2", color="#495057"),
                                            
                                            rx.divider(margin="1rem 0"),
                                            
                                            # Risposta data
                                            rx.hstack(
                                                rx.text(
                                                    "La tua risposta:",
                                                    weight="bold",
                                                    size="2",
                                                ),
                                                rx.text(
                                                    rx.cond(
                                                        QuizState.answers.get(q.number),
                                                        f"{QuizState.answers.get(q.number)} - {q.options.get(QuizState.answers.get(q.number), '')}",
                                                        "Non rispost",
                                                    ),
                                                    size="2",
                                                    color=rx.cond(
                                                        QuizState.answers.get(q.number) == q.correct_answer,
                                                        "#198754",  # Verde se corretta
                                                        "#dc3545",  # Rosso se errata
                                                    ),
                                                ),
                                                width="100%",
                                            ),
                                            
                                            # Risposta corretta
                                            rx.hstack(
                                                rx.text(
                                                    "Risposta corretta:",
                                                    weight="bold",
                                                    size="2",
                                                ),
                                                rx.text(
                                                    f"{q.correct_answer} - {q.options.get(q.correct_answer, '')}",
                                                    size="2",
                                                    color="#198754",
                                                ),
                                                width="100%",
                                            ),
                                            
                                            rx.divider(margin="1rem 0"),
                                            
                                            # Spiegazione
                                            rx.box(
                                                rx.vstack(
                                                    rx.text(
                                                        "Spiegazione:",
                                                        weight="bold",
                                                        size="2",
                                                        color="#495057",
                                                    ),
                                                    rx.text(
                                                        q.explanation,
                                                        size="1",
                                                        color="#6c757d",
                                                        line_height="1.6",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                ),
                                                background="rgba(255, 153, 0, 0.05)",
                                                padding="2",
                                                border_radius="md",
                                                border_left="4px solid #FF9900",
                                            ),
                                            
                                            spacing="2",
                                            width="100%",
                                        ),
                                        background=rx.cond(
                                            QuizState.answers.get(q.number) == q.correct_answer,
                                            "rgba(25, 135, 84, 0.05)",  # Verde chiaro
                                            "rgba(220, 53, 69, 0.05)",  # Rosso chiaro
                                        ),
                                        border_left=rx.cond(
                                            QuizState.answers.get(q.number) == q.correct_answer,
                                            "4px solid #198754",  # Verde
                                            "4px solid #dc3545",  # Rosso
                                        ),
                                        size="2",
                                        width="100%",
                                        margin_bottom="1rem",
                                    ),
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            max_height="60vh",
                            overflow_y="auto",
                            padding="2",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.box(height="0"),
                ),
                
                rx.divider(),
                
                # Bottoni
                rx.hstack(
                    rx.button(
                        "🏠 Ritorna alla Home",
                        size="3",
                        color_scheme="gray",
                        variant="outline",
                        on_click=[
                            QuizState.save_results(),
                            rx.redirect("/"),
                        ],
                    ),
                    rx.button(
                        "🔄 Ripeti " + rx.cond(QuizState.mode == "exam", "Esame", "Pratica"),
                        size="3",
                        color_scheme="blue",
                        on_click=[
                            QuizState.save_results(),
                            QuizState.reset_quiz(),
                            QuizState.load_quiz(QuizState.exam_id, QuizState.mode),
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
                # Header con timer
                rx.hstack(
                    rx.button(
                        "✕",
                        variant="ghost",
                        on_click=rx.redirect("/"),
                        size="3",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.text(
                            ExamState.available_exams.get(
                                QuizState.exam_id,
                                {}
                            ).get("code", "Quiz"),
                            size="2",
                            weight="bold",
                            color="#495057",
                        ),
                        rx.badge(
                            rx.cond(QuizState.mode == "exam", "🎯 ESAME", "📖 PRATICA"),
                            color_scheme=rx.cond(QuizState.mode == "exam", "orange", "blue"),
                            size="2",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    padding="3",
                    border_bottom="1px solid rgba(0, 0, 0, 0.1)",
                ),
                
                # Contenuto principale
                rx.vstack(
                    # Timer (se in exam mode)
                    rx.cond(
                        QuizState.mode == "exam",
                        rx.box(
                            rx.hstack(
                                rx.text(
                                    "⏱️ Tempo rimanente:",
                                    size="2",
                                    weight="bold",
                                    color="#495057",
                                ),
                                rx.text(
                                    QuizState.time_remaining_formatted,
                                    size="3",
                                    weight="bold",
                                    color=rx.cond(
                                        QuizState.time_remaining_seconds < 300,
                                        "#dc3545",
                                        "#0d6efd",
                                    ),
                                ),
                                width="100%",
                                justify_content="space-between",
                                align="center",
                            ),
                            padding="3",
                            background=rx.cond(
                                QuizState.time_remaining_seconds < 300,
                                "rgba(220, 53, 69, 0.1)",
                                "rgba(13, 110, 253, 0.05)",
                            ),
                            border_radius="md",
                            border="1px solid " + rx.cond(
                                QuizState.time_remaining_seconds < 300,
                                "rgba(220, 53, 69, 0.3)",
                                "rgba(13, 110, 253, 0.3)",
                            ),
                        ),
                        rx.box(height="0"),
                    ),
                    
                    progress_bar(),
                    
                    # Debug info
                    rx.text(
                        rx.cond(
                            QuizState.questions.length() > 0,
                            f"DEBUG: {QuizState.questions.length()} domande caricate (Modalità: {QuizState.mode})",
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
