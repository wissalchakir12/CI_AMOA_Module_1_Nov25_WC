"""
CIMR - Agent Dashboard
Professional UI for claim management and tracking
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional


# Configuration de la page
st.set_page_config(
    page_title="CIMR - Tableau de Bord Agent",
    page_icon="⬜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist CSS
st.markdown("""
<style>
    .stApp {
        background: #f8f9fa;
    }
    
    .dashboard-header {
        font-size: 2rem;
        font-weight: 300;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stat-card {
        background: white;
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 4px;
        text-align: center;
        border: 1px solid #e0e0e0;
        transition: border-color 0.2s ease;
    }
    
    .stat-card:hover {
        border-color: #4a5568;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 300;
        margin: 0.5rem 0;
        color: #1a1a1a;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 300;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .detail-section {
        background: white;
        padding: 2rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    .section-title {
        color: #2d3748;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button {
        background: #2d3748;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.6rem 1.5rem;
        font-size: 0.9rem;
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
    
    [data-testid="stSidebar"] .stMarkdown {
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


def get_all_claims() -> List[Dict]:
    """Fetch all claims from the API"""
    api_url = "http://localhost:8000/api/claims/"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Erreur lors de la récupération des réclamations: {response.status_code}")
            return []
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de se connecter à l'API. Veuillez vous assurer que le serveur est en cours d'exécution sur http://localhost:8000")
        return []
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return []


def get_claim_details(ticket_id: str) -> Optional[Dict]:
    """Fetch specific claim details"""
    api_url = f"http://localhost:8000/api/claims/{ticket_id}"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la récupération de la réclamation: {str(e)}")
        return None


def format_priority(priority: Optional[int]) -> str:
    """Format priority"""
    if priority is None:
        return "N/A"
    
    labels = {5: "Critique", 4: "Élevée", 3: "Moyenne", 2: "Faible", 1: "Minimale"}
    return labels.get(priority, f"Priorité {priority}")


def format_status(status: Optional[str]) -> str:
    """Format status"""
    if not status:
        return "Inconnu"
    
    labels = {
        "New": "Nouvelle",
        "In progress": "En Cours",
        "Resolved": "Résolue"
    }
    return labels.get(status, status)


def format_category(category: Optional[str]) -> str:
    """Format category in French"""
    if not category:
        return "N/A"
    
    labels = {
        "Payment": "Paiement",
        "Affiliation": "Affiliation",
        "Contribution": "Cotisation",
        "Death": "Décès",
        "Technical": "Technique"
    }
    return labels.get(category, category)


def main():
    # En-tête
    st.markdown('<div class="dashboard-header">CIMR — Tableau de Bord Agent</div>', unsafe_allow_html=True)
    
    # Bouton de rafraîchissement
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Actualiser", use_container_width=True):
            st.rerun()
    
    # Barre latérale - Navigation et Filtres
    st.sidebar.markdown("")
    if st.sidebar.button("Accueil", use_container_width=True, key="nav_home"):
        st.switch_page("app.py")
    if st.sidebar.button("Portail Membre", use_container_width=True, key="nav_member"):
        st.switch_page("pages/1_Member_Portal.py")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtres")
    
    status_filter = st.sidebar.selectbox(
        "Statut",
        ["All", "New", "In progress", "Resolved"],
        key="status_filter"
    )
    
    priority_filter = st.sidebar.selectbox(
        "Priorité",
        ["All", "Critical (5)", "High (4)", "Medium (3)", "Low (2)", "Minimal (1)"],
        key="priority_filter"
    )
    
    category_options_fr = ["All", "Paiement", "Affiliation", "Cotisation", "Décès", "Technique"]
    category_options_en = ["All", "Payment", "Affiliation", "Contribution", "Death", "Technical"]
    category_filter_mapping = dict(zip(category_options_fr, category_options_en))
    
    category_filter_fr = st.sidebar.selectbox(
        "Catégorie",
        category_options_fr,
        key="category_filter"
    )
    
    # Map French display to English value for filtering
    category_filter = category_filter_mapping[category_filter_fr]
    
    # Récupérer les réclamations
    with st.spinner("Chargement des réclamations..."):
        claims = get_all_claims()
    
    if not claims:
        st.warning("Aucune réclamation trouvée. Commencez par soumettre une réclamation via le Portail Membre.")
        return
    
    # Appliquer les filtres
    filtered_claims = claims
    
    if status_filter != "All":
        filtered_claims = [c for c in filtered_claims if c.get('status') == status_filter]
    
    if priority_filter != "All":
        priority_num = int(priority_filter[-2])
        filtered_claims = [c for c in filtered_claims if c.get('priority') == priority_num]
    
    if category_filter != "All":
        filtered_claims = [c for c in filtered_claims if c.get('category') == category_filter]
    
    # Statistiques
    st.markdown("## Statistiques")
    
    total_claims = len(claims)
    new_claims = len([c for c in claims if c.get('status') == 'New'])
    in_progress = len([c for c in claims if c.get('status') == 'In progress'])
    resolved = len([c for c in claims if c.get('status') == 'Resolved'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_claims}</div>
            <div class="stat-label">Réclamations Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{new_claims}</div>
            <div class="stat-label">Nouvelles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{in_progress}</div>
            <div class="stat-label">En Cours</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{resolved}</div>
            <div class="stat-label">Résolues</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Table des réclamations
    st.markdown(f"## Réclamations ({len(filtered_claims)} trouvées)")
    
    if filtered_claims:
        # Sort claims by created_at date (most recent first)
        sorted_claims = sorted(
            filtered_claims, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        # Préparer les données pour le tableau
        table_data = []
        for claim in sorted_claims:
            # Format date exactly as stored in database without timezone conversion
            created_at = claim.get('created_at', 'N/A')
            if created_at and created_at != 'N/A':
                try:
                    # Parse and format without timezone conversion - keep original date/time
                    if 'T' in created_at:
                        # ISO format: split date and time parts
                        date_part = created_at.split('T')[0]  # YYYY-MM-DD
                        time_part = created_at.split('T')[1].split('.')[0] if '.' in created_at else created_at.split('T')[1].split('Z')[0]
                        # Convert to DD/MM/YYYY HH:MM
                        year, month, day = date_part.split('-')
                        hour_min = time_part[:5]  # Get HH:MM
                        created_at_formatted = f"{day}/{month}/{year} {hour_min}"
                    else:
                        created_at_formatted = created_at
                except:
                    created_at_formatted = created_at[:16] if len(created_at) > 16 else created_at
            else:
                created_at_formatted = 'N/A'
            
            table_data.append({
                "ID Ticket": claim.get('ticket_id', 'N/A'),
                "Membre": claim.get('member_name', 'N/A'),
                "Catégorie": format_category(claim.get('category')),
                "Priorité": format_priority(claim.get('priority')),
                "Statut": format_status(claim.get('status')),
                "Créé le": created_at_formatted
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Section des détails
        st.markdown("## Consulter les Détails")
        
        selected_ticket = st.selectbox(
            "Sélectionner l'ID du ticket pour consulter les détails",
            [c.get('ticket_id') for c in filtered_claims],
            key="selected_ticket"
        )
        
        if st.button("Afficher les Détails"):
            claim_details = get_claim_details(selected_ticket)
            
            if claim_details:
                st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="section-title">Informations de Base</div>', unsafe_allow_html=True)
                    st.write(f"**Membre:** {claim_details.get('member_name', 'N/A')}")
                    st.write(f"**CIN:** {claim_details.get('member_id', 'N/A')}")
                    st.write(f"**Catégorie:** {format_category(claim_details.get('category'))}")
                    st.write(f"**Priorité:** {format_priority(claim_details.get('priority'))}")
                    st.write(f"**Statut:** {format_status(claim_details.get('status'))}")
                
                with col2:
                    st.markdown('<div class="section-title">Analyse</div>', unsafe_allow_html=True)
                    confidence = claim_details.get('confidence')
                    st.write(f"**Confiance:** {confidence if confidence is not None else 'N/A'}")
                    
                    sla_hours = claim_details.get('sla_hours')
                    st.write(f"**SLA (heures):** {sla_hours if sla_hours is not None else 'N/A'}")
                    
                    assigned_agent = claim_details.get('assigned_agent')
                    st.write(f"**Agent Assigné:** {assigned_agent if assigned_agent else 'Aucun'}")
                    
                    requires_attention = claim_details.get('requires_attention')
                    st.write(f"**Requiert Attention:** {'Oui' if requires_attention else 'Non'}")
                
                st.markdown("### Message Original")
                st.text_area("Message", claim_details.get('message', ''), height=100, disabled=True, label_visibility="hidden")
                
                if claim_details.get('draft_response'):
                    st.markdown("### Réponse Générée par l'IA")
                    st.text_area("Réponse IA", claim_details.get('draft_response', ''), height=200, disabled=True, label_visibility="hidden")
                    
                    quality_score = claim_details.get('response_quality_score')
                    response_language = claim_details.get('response_language')
                    
                    col_resp1, col_resp2 = st.columns(2)
                    with col_resp1:
                        st.write(f"**Score de Qualité:** {quality_score if quality_score is not None else 'N/A'}")
                    with col_resp2:
                        st.write(f"**Langue:** {response_language if response_language else 'N/A'}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucune réclamation ne correspond aux filtres sélectionnés.")


if __name__ == "__main__":
    main()
