"""Pagina classifica leaderboard."""
from __future__ import annotations

from typing import Dict, List

import reflex as rx
from aws_simulator.state import UserState
from aws_simulator.database import get_db
from aws_simulator.config import EXAMS


class LeaderboardState(rx.State):
    """State per la classifica."""
    leaderboard_data: List[Dict] = []
    
    def load_leaderboard(self):
        """Carica la classifica."""
        db = get_db()
        self.leaderboard_data = db.get_leaderboard("saa_c03", mode="exam")

  
  
def leaderboard_row(rank: int, entry: Dict) -> rx.Component:
    """Riga della classifica."""
    return rx.box(
        rx.hstack(
            # Ranking
            rx.box(
                rx.text(
                    f"#{rank}",
                    font_weight="bold",
                    size="3",
                    color="#0d6efd",
                    text_align="center",
                ),
                width="50px",
                min_width="50px",
            ),
            
            # Nome utente
            rx.box(
                rx.text(
                    entry["name"],
                    weight="bold",
                    size="2",
                    color="#0a1428",
                ),
                width="200px",
                min_width="200px",
            ),
            
            # Score
            rx.box(
                rx.hstack(
                    rx.text(
                        entry["score"].to(str) + "%",
                        font_weight="bold",
                        size="2",
                        color="#198754",
                    ),
                    rx.text(
                        "(" + entry["correct"].to(str) + "/" + entry["total"].to(str) + ")",
                        size="1",
                        color="#6c757d",
                    ),
                    spacing="2",
                ),
                width="150px",
                min_width="150px",
            ),
            
            rx.spacer(),
            
            # Data
            rx.text(
                entry["date"],
                size="1",
                color="#6c757d",
                text_align="right",
            ),
            
            width="100%",
            padding="1rem",
            border_bottom="1px solid #e9ecef",
            align="center",
        ),
        width="100%",
    )


@rx.page(route="/leaderboard", title="Classifica – AWS Simulator")
def leaderboard_page() -> rx.Component:
    """Pagina classifica."""
    
    return rx.vstack(
        # Top gradient bar
        rx.box(
            height="4px",
            background="linear-gradient(90deg, #FF9900 0%, #0d6efd 100%)",
        ),
        
        # Main content
        rx.vstack(
            # Header
            rx.hstack(
                rx.button(
                    "← Indietro",
                    variant="ghost",
                    on_click=rx.redirect("/"),
                    size="2",
                ),
                rx.spacer(),
                rx.heading(
                    "🏆 Classifica",
                    size="6",
                    color="#0a1428",
                    font_weight="800",
                ),
                rx.spacer(),
                rx.box(width="auto"),
                width="100%",
                padding="2rem",
                border_bottom="1px solid rgba(0, 0, 0, 0.1)",
                align="center",
            ),
            
            # Contenuto
            rx.vstack(
                rx.text(
                    f"Top 10 - {EXAMS.get('saa_c03', {}).get('code', 'SAA-C03')}",
                    size="3",
                    weight="bold",
                    color="#0a1428",
                ),
                
                rx.cond(
                    LeaderboardState.leaderboard_data.length() > 0,
                    rx.vstack(
                        # Header tabella
                        rx.box(
                            rx.hstack(
                                rx.box(
                                    rx.text("#", weight="bold", size="2"),
                                    width="50px",
                                    min_width="50px",
                                ),
                                rx.box(
                                    rx.text("Utente", weight="bold", size="2"),
                                    width="200px",
                                    min_width="200px",
                                ),
                                rx.box(
                                    rx.text("Score", weight="bold", size="2"),
                                    width="150px",
                                    min_width="150px",
                                ),
                                rx.spacer(),
                                rx.text("Data", weight="bold", size="2"),
                                width="100%",
                                padding="1rem",
                                background="#f8f9fa",
                                border_bottom="2px solid #dee2e6",
                                align="center",
                            ),
                            width="100%",
                        ),
                        
                        # Righe classifica
                        rx.foreach(
                            LeaderboardState.leaderboard_data.to(List[Dict]),
                            lambda entry, idx: leaderboard_row(idx + 1, entry),
                        ),
                        
                        spacing="0",
                        width="100%",
                        border_radius="lg",
                        border="1px solid #dee2e6",
                        overflow="hidden",
                    ),
                    rx.box(
                        rx.text(
                            "Nessun risultato. Completa un esame per apparire in classifica!",
                            size="2",
                            color="#6c757d",
                            text_align="center",
                        ),
                        padding="2rem",
                        text_align="center",
                        width="100%",
                    ),
                ),
                
                spacing="4",
                padding="2rem 1rem",
                width="100%",
                max_width="1000px",
                margin_x="auto",
            ),
            
            spacing="0",
            width="100%",
            min_height="100vh",
            background="linear-gradient(135deg, #f8f9fa 0%, #e8f0fe 100%)",
            on_mount=LeaderboardState.load_leaderboard,
        ),
        
        spacing="0",
        width="100%",
    )
