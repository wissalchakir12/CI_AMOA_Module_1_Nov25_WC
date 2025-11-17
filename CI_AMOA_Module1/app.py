"""
CIMR Claims Automation - Main Application
Automated claims processing system
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="CIMR - Gestion des Réclamations",
    page_icon="⬜",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CIMR - Système de Gestion des Réclamations v1.0"
    }
)

# Minimalist professional CSS
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Header styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 4rem;
        font-weight: 300;
    }
    
    /* Landing cards */
    .landing-card {
        background: white;
        padding: 3rem 2.5rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        transition: all 0.2s ease;
        margin: 1rem 0;
        min-height: 280px;
    }
    
    .landing-card:hover {
        border-color: #4a5568;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 400;
        color: #2d3748;
        margin-bottom: 1rem;
        text-align: left;
    }
    
    .feature-description {
        color: #718096;
        line-height: 1.7;
        text-align: left;
        font-size: 0.95rem;
        font-weight: 300;
    }
    
    /* Capability boxes */
    .capability-box {
        background: white;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        margin: 0.8rem 0;
        transition: all 0.2s ease;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .capability-box:hover {
        border-color: #4a5568;
    }
    
    .capability-box h4 {
        color: #2d3748;
        margin-bottom: 0.75rem;
        font-weight: 400;
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .capability-box p {
        color: #718096;
        font-size: 0.85rem;
        font-weight: 300;
        line-height: 1.6;
        flex-grow: 1;
    }
    
    /* Workflow steps */
    .workflow-step {
        background: white;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 0.8rem 0;
        border: 1px solid #e0e0e0;
        border-left: 3px solid #2d3748;
        transition: all 0.2s ease;
    }
    
    .workflow-step:hover {
        border-left-color: #4a5568;
    }
    
    .workflow-step strong {
        color: #2d3748;
        font-weight: 400;
    }
    
    .workflow-step p {
        color: #718096;
        font-size: 0.9rem;
        font-weight: 300;
    }
    
    /* Section headers */
    .section-header {
        color: #2d3748;
        font-size: 1.3rem;
        font-weight: 400;
        margin: 3rem 0 1.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Info box */
    .info-box {
        background: white;
        padding: 2rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
    }
    
    .info-box h3 {
        color: #2d3748;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    .info-box p {
        color: #718096;
        line-height: 1.7;
        font-weight: 300;
    }
    
    /* Buttons */
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
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a202c;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background-color: #2d3748;
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


def main():
    # Sidebar configuration
    with st.sidebar:
        st.markdown("")
        if st.button("Portail Membre", use_container_width=True, key="nav_member"):
            st.switch_page("pages/1_Member_Portal.py")
        if st.button("Tableau de Bord Agent", use_container_width=True, key="nav_agent"):
            st.switch_page("pages/2_Agent_Dashboard.py")
    
    # Main header
    st.markdown('<div class="main-header">CIMR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Système de Gestion Automatisée des Réclamations</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="landing-card">
            <div class="feature-title">Portail Membre</div>
            <div class="feature-description">
                Interface pour soumettre vos réclamations. 
                Notre système d'intelligence artificielle traite et répond 
                automatiquement à chaque demande avec précision.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au Portail Membre", use_container_width=True):
            st.switch_page("pages/1_Member_Portal.py")
    
    with col2:
        st.markdown("""
        <div class="landing-card">
            <div class="feature-title">Tableau de Bord Agent</div>
            <div class="feature-description">
                Supervision en temps réel. Analysez les données IA, 
                suivez les réponses générées et surveillez l'état de chaque réclamation 
                avec précision.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au Tableau de Bord", use_container_width=True):
            st.switch_page("pages/2_Agent_Dashboard.py")
    
    # System capabilities
    st.markdown('<div class="section-header">Capacités du Système</div>', unsafe_allow_html=True)
    
    capabilities = [
        ("Traitement par IA", "6 agents IA spécialisés orchestrés pour un traitement automatique"),
        ("Support Multilingue", "Français, Arabe et Anglais"),
        ("Temps Réel", "Suivi instantané du traitement de chaque réclamation"),
        ("Analytics Avancées", "Scoring de priorité, SLA dynamique et conformité ACAPS"),
        ("Réponses Personnalisées", "Génération automatique de réponses professionnelles"),
        ("Conformité Totale", "Respect automatique des réglementations ACAPS")
    ]
    
    cols = st.columns(3, gap="medium")
    for idx, (title, desc) in enumerate(capabilities):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="capability-box">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Workflow steps
    st.markdown('<div class="section-header">Processus de Traitement</div>', unsafe_allow_html=True)
    
    steps = [
        ("01", "Réception de la Réclamation", "Le membre soumet sa réclamation via le portail web avec ses informations et description détaillée"),
        ("02", "Analyse Intelligente", "Extraction automatique des informations clés (nom, CIN, sujet) à partir du message"),
        ("03", "Classification Automatique", "Identification de la catégorie (Paiement, Affiliation, Contribution, Décès, Technique)"),
        ("04", "Évaluation de l'Urgence", "Attribution d'un score de priorité (1-5) et calcul du délai de traitement (SLA)"),
        ("05", "Vérification de Conformité", "Contrôle automatique du respect des réglementations ACAPS"),
        ("06", "Génération de Réponse", "Rédaction automatique d'une réponse personnalisée dans la langue du membre"),
        ("07", "Suivi et Mise à Jour", "Mise à jour du statut et notification du traitement de la réclamation")
    ]
    
    for number, title, desc in steps:
        st.markdown(f"""
        <div class="workflow-step">
            <strong>{number}. {title}</strong>
            <p style="margin-top: 0.5rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # About section
    st.markdown('<div class="section-header">À Propos</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>CIMR — Caisse Interprofessionnelle Marocaine de Retraite</h3>
        <p>
            Ce système de gestion automatisée révolutionne le traitement des réclamations en combinant 
            intelligence artificielle et efficacité opérationnelle. Réduction jusqu'à 70% des délais 
            de traitement pour les réclamations simples, avec conformité totale aux réglementations ACAPS.
        </p>
        <p style="margin-top: 1rem;">
            Traitement automatisé • Réponses instantanées • Suivi en temps réel • Conformité garantie
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
        <p style="font-size: 0.9rem; font-weight: 300;">© 2025 CIMR — Système de Gestion des Réclamations v1.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
