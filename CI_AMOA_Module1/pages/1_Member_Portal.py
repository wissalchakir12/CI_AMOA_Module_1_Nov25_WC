"""
CIMR - Member Portal
Professional UI for claim submission
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional


# Configuration de la page
st.set_page_config(
    page_title="CIMR - Portail Membre",
    page_icon="⬜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS
st.markdown("""
<style>
    .stApp {
        background: #f8f9fa;
    }
    
    .main-header {
        font-size: 2rem;
        font-weight: 300;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .form-section {
        background: white;
        padding: 3rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .section-header {
        color: #2d3748;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stTextInput>div>div>input {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 0.75rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #4a5568;
        box-shadow: none;
    }
    
    .stTextArea>div>div>textarea {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        transition: border-color 0.2s ease;
    }
    
    .stTextArea>div>div>textarea:focus {
        border-color: #4a5568;
        box-shadow: none;
    }
    
    .success-message {
        background: white;
        color: #2d3748;
        padding: 2.5rem;
        border-radius: 4px;
        margin: 2rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .success-message h3 {
        margin: 0 0 1rem 0;
        font-size: 1.3rem;
        font-weight: 400;
        color: #2d3748;
    }
    
    .info-box {
        background: white;
        color: #718096;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0 2rem 0;
        border: 1px solid #e0e0e0;
        border-left: 3px solid #2d3748;
    }
    
    .ticket-display {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 4px;
        border: 1px solid #2d3748;
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        font-weight: 500;
        color: #2d3748;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stButton>button {
        background: #2d3748;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.75rem 2rem;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background: #4a5568;
    }
    
    /* Primary button override */
    .stButton>button[kind="primary"] {
        background: #2d3748;
        color: white;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #4a5568;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a202c;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Hide default page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Sidebar buttons - smaller text */
    [data-testid="stSidebar"] .stButton>button {
        font-size: 0.85rem;
        padding: 0.6rem 1rem;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# Initialiser le state de session
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'ticket_id' not in st.session_state:
    st.session_state.ticket_id = None


def submit_claim(member_name: str, member_id: str, message: str, member_email: str = None, channel: str = "Web") -> Optional[str]:
    """
    Submit a new claim to the backend API
    """
    api_url = "http://localhost:8000/api/claims/"

    payload = {
        "member_name": member_name,
        "member_id": member_id,
        "channel": channel,
        "message": message
    }

    # Add email if provided
    if member_email and member_email.strip():
        payload["member_email"] = member_email
    
    try:
        response = requests.post(api_url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                content = data.get('data', {})
                workflow_result = json.loads(content.get('content', '{}'))
                ticket_id = workflow_result.get('ticket_id')
                return ticket_id
            else:
                st.error(f"❌ Erreur: {data.get('message', 'Erreur inconnue')}")
                return None
        else:
            st.error(f"❌ Erreur API: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de se connecter à l'API. Veuillez vous assurer que le serveur est en cours d'exécution sur http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Délai d'attente dépassé. Le workflow prend plus de temps que prévu.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return None


def main():
    # Sidebar configuration
    with st.sidebar:
        st.markdown("")
        if st.button("Accueil", use_container_width=True, key="nav_home"):
            st.switch_page("app.py")
        if st.button("Tableau de Bord Agent", use_container_width=True, key="nav_agent"):
            st.switch_page("pages/2_Agent_Dashboard.py")
    
    # En-tête
    st.markdown('<div class="main-header">CIMR — Portail Membre</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Soumettez votre réclamation</div>', unsafe_allow_html=True)
    
    # Encadré d'information
    st.markdown("""
    <div class="info-box">
        Soumettez votre réclamation et notre système d'intelligence artificielle la traitera automatiquement 
        avec une réponse professionnelle et personnalisée.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for form persistence
    if 'member_name' not in st.session_state:
        st.session_state.member_name = ''
    if 'member_id' not in st.session_state:
        st.session_state.member_id = ''
    if 'member_email' not in st.session_state:
        st.session_state.member_email = ''
    if 'message' not in st.session_state:
        st.session_state.message = ''
    
    # Formulaire principal
    with st.form("formulaire_reclamation", clear_on_submit=False):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Informations du Membre</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            member_name = st.text_input(
                "Nom et Prénom *",
                value=st.session_state.member_name,
                placeholder="Ex: Ahmed Benali",
                help="Votre nom complet",
                key="member_name_form"
            )
        
        with col2:
            member_id = st.text_input(
                "CIN / Numéro d'adhérent *",
                value=st.session_state.member_id,
                placeholder="Ex: C123456789",
                help="Votre numéro d'identification",
                key="member_id_form"
            )

        # Email field (optional)
        member_email = st.text_input(
            "Adresse Email (optionnel)",
            value=st.session_state.member_email,
            placeholder="exemple@email.com",
            help="Pour recevoir des notifications par email sur l'état de votre réclamation",
            key="member_email_form"
        )

        st.markdown('<div class="section-header">Détails de la Réclamation</div>', unsafe_allow_html=True)
        
        # Info about automatic categorization
        st.info("Note: La catégorie de votre réclamation sera automatiquement déterminée par notre système d'IA.")
        
        # Message
        message = st.text_area(
            "Description de votre réclamation *",
            value=st.session_state.message,
            height=150,
            placeholder="Décrivez votre réclamation en détail. Mentionnez toute information pertinente, dates, montants, etc.",
            help="Fournissez autant de détails que possible pour un traitement rapide et efficace",
            key="message_form"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bouton de soumission
        submitted = st.form_submit_button(
            "Soumettre la Réclamation",
            use_container_width=True
        )
        
        if submitted:
            # Validation
            if not member_name or not member_id or not message:
                st.warning("⚠️ Veuillez remplir tous les champs obligatoires (marqués d'un *)")
            else:
                # Store form values in session state
                st.session_state.member_name = member_name
                st.session_state.member_id = member_id
                st.session_state.member_email = member_email
                st.session_state.message = message

                with st.spinner("⏳ Traitement en cours... Notre système IA analyse votre réclamation avec attention"):
                    ticket_id = submit_claim(member_name, member_id, message, member_email)
                    
                    if ticket_id:
                        st.session_state.submitted = True
                        st.session_state.ticket_id = ticket_id
                        st.rerun()
    
    # Message de succès
    if st.session_state.submitted and st.session_state.ticket_id:
        st.markdown(f"""
        <div class="success-message">
            <h3>Réclamation Soumise avec Succès</h3>
            <p style="font-size: 0.95rem; margin: 1rem 0; color: #718096;">
                Identifiant de réclamation:
            </p>
            <div class="ticket-display">{st.session_state.ticket_id}</div>
            <p style="font-size: 0.95rem; margin-top: 1.5rem; color: #718096; line-height: 1.7;">
                Votre réclamation est en cours de traitement par notre système IA intelligent. 
                Vous recevrez une réponse professionnelle et personnalisée dans les plus brefs délais.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Boutons d'action
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            if st.button("Consulter les Réclamations"):
                st.switch_page("pages/2_Agent_Dashboard.py")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Soumettre une Autre Réclamation"):
                st.session_state.submitted = False
                st.session_state.ticket_id = None
                # Clear form fields
                st.session_state.member_name = ''
                st.session_state.member_id = ''
                st.session_state.member_email = ''
                st.session_state.message = ''
                st.rerun()


if __name__ == "__main__":
    main()
