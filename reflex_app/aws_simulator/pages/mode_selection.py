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
    exam_info: dict = None,
) -> rx.Component:
    """Card per una modalità di quiz. Info box mostrato solo per modalità exam."""
    
    # Info box che verrà mostrato solo per modalità exam
    # Se exam_info è una Var reattiva, buildamo il box solo se è una Var (not None at Python level)
    if exam_info is None:
        info_box = rx.box()  # Empty box for practice mode
    else:
        info_box = rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("ℹ️ Dettagli esame:", size="1", weight="bold", color="#0d6efd"),
                    rx.spacer(),
                    width="100%",
                ),
                rx.text(
                    f"📝 Domande a risposta multipla: ~{exam_info.get('multiple_choice', 'N/D')}",
                    size="1",
                    color="#495057",
                ),
                rx.text(
                    f"⏱️  Tempo totale: {exam_info.get('duration', 'N/D')} minuti ({exam_info.get('duration_with_esl', 'N/D')} con ESL +30)",
                    size="1",
                    color="#495057",
                ),
                rx.text(
                    f"🎯 Nessun punteggio parziale per risposte multiple",
                    size="1",
                    color="#495057",
                ),
                spacing="2",
                width="100%",
            ),
            background="#e7f5ff",
            padding="1rem",
            border_radius="md",
            border="1px solid #b3d9ff",
            width="100%",
        )
    
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
            
            # Info box per modalità exam
            info_box,
            
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
                        exam_info=None,
                    ),
                    
                    # Simulazione Esame - Info dinamica dall'esame selezionato
                    mode_card(
                        title="Simulazione Esame",
                        emoji="🎯",
                        description="Prova reale con timer e domande casuali",
                        details=[
                            "65 domande casuali",
                            rx.cond(
                                ExamState.available_exams[ExamState.selected_exam].get("duration") == 180,
                                "Tempo limitato (180 min)",
                                "Tempo limitato (130 min)",
                            ),
                            "Le risposte corrette si vedono alla fine",
                            "Simulazione realistica",
                            "Risultato salvato in classifica",
                        ],
                        color_scheme="orange",
                        mode="exam",
                        exam_info=rx.cond(
                            ExamState.selected_exam != None,
                            {
                                "multiple_choice": rx.cond(
                                    ExamState.available_exams[ExamState.selected_exam].get("duration") == 180,
                                    "25-30 su 75",
                                    "10-15 su 65",
                                ),
                                "duration": ExamState.available_exams[ExamState.selected_exam].get("duration", 130),
                                "duration_with_esl": ExamState.available_exams[ExamState.selected_exam].get("duration_esl", 160),
                            },
                            None,
                        ),
                    ),
                    
                    columns=rx.cond(
                        rx.breakpoints(initial="1", sm="1", md="2", lg="2", xl="2"),
                        "2",
                        "1",
                    ),
                    spacing="6",
                    width="100%",
                ),
                
                # Sezione info ESL +30 minuti
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "ℹ️ Diritti ESL - Tempo Aggiuntivo",
                            size="4",
                            color="#0a1428",
                            font_weight="700",
                        ),
                        rx.text(
                            "Se sei un candidato non madrelingua inglese (inclusi gli italiani), hai diritto a 30 minuti di tempo aggiuntivo per TUTTI gli esami AWS.",
                            size="2",
                            color="#495057",
                            line_height="1.6",
                        ),
                        rx.divider(),
                        rx.hstack(
                            rx.vstack(
                                rx.heading("📋 Come funziona:", size="3", color="#0d6efd", font_weight="700"),
                                rx.text("✓ Richiesta una sola volta (vale per tutti gli esami futuri)", size="1", color="#495057"),
                                rx.text("✓ Approvazione automatica e immediata", size="1", color="#495057"),
                                rx.text("✓ Nessuna documentazione richiesta", size="1", color="#495057"),
                                rx.text("✓ Non serve certificato di lingua", size="1", color="#495057"),
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.heading("⏱️ Tempi per questo esame:", size="3", color="#0d6efd", font_weight="700"),
                                rx.cond(
                                    ExamState.available_exams[ExamState.selected_exam].get("duration") == 180,
                                    rx.vstack(
                                        rx.text("• Senza ESL: 180 minuti (3h)", size="1", color="#495057"),
                                        rx.text("• Con ESL: 210 minuti (3h 30m)", size="1", color="#495057"),
                                        rx.text("• Differenza: +30 minuti", size="1", color="#198754", weight="bold"),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("• Senza ESL: 130 minuti (2h 10m)", size="1", color="#495057"),
                                        rx.text("• Con ESL: 160 minuti (2h 40m)", size="1", color="#495057"),
                                        rx.text("• Differenza: +30 minuti", size="1", color="#198754", weight="bold"),
                                        spacing="1",
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.callout(
                            rx.text(
                                "⚠️ IMPORTANTE: Richiedi ESL nel tuo account AWS PRIMA di prenotare l'esame. Se prenoti prima, dovrai annullarlo e riprenotarlo dopo l'approvazione.",
                                size="1",
                                color="#856404",
                            ),
                            icon="triangle_alert",
                            color_scheme="orange",
                            role="alert",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    background="#fffbea",
                    padding="2rem",
                    border_radius="lg",
                    border="1px solid #ffeaa7",
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
