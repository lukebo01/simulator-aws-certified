"""Pagina di selezione/creazione profili utente."""
from __future__ import annotations

import reflex as rx
from aws_simulator.state import UserState
from aws_simulator.database import get_db


class ProfileInputState(rx.State):
    """State per l'input del nuovo profilo."""
    new_profile_name: str = ""
    
    def set_new_profile_name(self, value: str) -> None:
        """Aggiorna il nome del nuovo profilo."""
        self.new_profile_name = value


@rx.page(route="/profiles", title="Profili – AWS Simulator")
def profile_selection_page() -> rx.Component:
    """Pagina di selezione profili."""
    db = get_db()
    profiles = db.get_all_profiles()
    
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
                    "← Home",
                    variant="ghost",
                    on_click=rx.redirect("/"),
                    size="2",
                ),
                rx.spacer(),
                rx.heading(
                    "👤 Profili Utente",
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
                # Sezione: Profili esistenti
                rx.vstack(
                    rx.heading(
                        "Seleziona un profilo",
                        size="4",
                        color="#0a1428",
                    ),
                    
                    rx.cond(
                        len(profiles) > 0,
                        rx.grid(
                            rx.vstack(
                                *[
                                    rx.card(
                                        rx.vstack(
                                            rx.heading(
                                                profile.name,
                                                size="4",
                                                color="#0a1428",
                                                font_weight="700",
                                            ),
                                            
                                            rx.text(
                                                f"Creato: {profile.created_at[:10]}",
                                                size="1",
                                                color="#6c757d",
                                            ),
                                            
                                            rx.text(
                                                f"Ultimo accesso: {profile.last_login[:10]}",
                                                size="1",
                                                color="#6c757d",
                                            ),
                                            
                                            rx.button(
                                                "Seleziona",
                                                width="100%",
                                                size="2",
                                                color_scheme="blue",
                                                on_click=[
                                                    UserState.select_profile(profile.id),
                                                    rx.redirect("/"),
                                                ],
                                            ),
                                            
                                            spacing="2",
                                            width="100%",
                                        ),
                                        width="100%",
                                        background="white",
                                        border_radius="lg",
                                        border="1px solid #e9ecef",
                                        box_shadow="0 2px 8px rgba(0, 0, 0, 0.08)",
                                        _hover={
                                            "box_shadow": "0 8px 16px rgba(0, 0, 0, 0.12)",
                                            "transition": "all 0.3s ease",
                                        },
                                    )
                                    for profile in profiles
                                ]
                            ),
                            columns="3",
                            spacing="4",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "Nessun profilo trovato. Creane uno nuovo!",
                                size="2",
                                color="#6c757d",
                                text_align="center",
                            ),
                            padding="2rem",
                            text_align="center",
                        ),
                    ),
                    
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(),
                
                # Sezione: Crea nuovo profilo
                rx.vstack(
                    rx.heading(
                        "Crea un nuovo profilo",
                        size="4",
                        color="#0a1428",
                    ),
                    
                    rx.input(
                        placeholder="Nome profilo",
                        value=ProfileInputState.new_profile_name,
                        on_change=lambda value: ProfileInputState.set_new_profile_name(value),
                        size="3",
                        width="100%",
                    ),
                    
                    rx.button(
                        "✨ Crea Profilo",
                        size="3",
                        color_scheme="green",
                        width="100%",
                        on_click=lambda: [
                            UserState.create_new_profile(ProfileInputState.new_profile_name),
                            ProfileInputState.set_new_profile_name(""),
                            rx.redirect("/"),
                        ],
                    ),
                    
                    spacing="3",
                    width="100%",
                    max_width="400px",
                ),
                
                spacing="6",
                padding="2rem 1rem",
                width="100%",
                max_width="1200px",
                margin_x="auto",
            ),
            
            spacing="0",
            width="100%",
            min_height="100vh",
            background="linear-gradient(135deg, #f8f9fa 0%, #e8f0fe 100%)",
        ),
        
        spacing="0",
        width="100%",
    )
