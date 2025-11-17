# Automatisation des Réclamations CIMR v1 - Référence du Projet

## 🎯 Vue d'Ensemble du Projet

Le Module de Traitement Automatique des Réclamations par IA pour la CIMR (Caisse Interprofessionnelle Marocaine de Retraite) est un système intelligent et automatisé conçu pour numériser et rationaliser le workflow complet de gestion des réclamations. Le système dispose d'un portail pour les membres permettant la soumission de réclamations et d'un tableau de bord agent interne pour la gestion des réclamations, tous deux construits avec Streamlit.

### 🎯 Objectifs Spécifiques CIMR
- **Réduire les délais de traitement** (jusqu'à -70% pour les réclamations simples)
- **Améliorer la satisfaction des adhérents** (réponses automatiques + suivi proactif)
- **Optimiser la traçabilité et la conformité** avec les processus requis par l'ACAPS
- **Améliorer l'efficacité interne** (moins d'erreurs humaines, gestion centralisée des tickets)

### 🔗 Intégrations
Ce module s'intègre avec :
- **Interface Streamlit** : Portail membre professionnel et tableau de bord agent
- **Airtable** : CRM léger et base de données pour la gestion des réclamations
- **Azure OpenAI** : Classification IA, priorisation et génération de réponses
- Systèmes internes CIMR (dossiers de pension, cotisations, affiliations)

## 🏗️ 1. Architecture Globale (V1)

| Couche | Composants | Outils / Tech | Notes |
|--------|------------|---------------|-------|
| **Frontend (UI)** | Formulaire web + Tableau de bord Agent | Streamlit ou application React légère | Interface simple pour les membres + agents internes |
| **Backend (Core API)** | FastAPI (Python) | FastAPI | Gère la soumission des réclamations, le routage, les mises à jour de statut |
| **Couche Agente** | Agents IA orchestrés via Agno | Agno Framework | Gère les flux : réception → classification → résolution |
| **Couche Données** | Airtable | Airtable REST API | Fonctionne comme un CRM léger + base de tickets |
| **Couche NLP & LLM** | Azure OpenAI / OpenAI API | GPT-4o-mini ou GPT-4-turbo | Utilisé pour la classification NLP et la rédaction de réponses |
| **Intégrations** | Canaux futurs | WhatsApp / Email (v2+) | Prévu pour expansion future |

## 🧩 2. Architecture du Module Fonctionnel

| Sous-module | Description | Agents IA Impliqués |
|-------------|-------------|---------------------|
| **1. Collection & Classification** | Réception automatique des réclamations et catégorisation basée sur le contenu et le canal | InputParserAgent, NLPClassifierAgent |
| **2. Analyse & Priorisation** | Analyse du type, de l'urgence et de la gravité de la réclamation | PriorityScoringAgent, ComplianceCheckerBot |
| **3. Résolution & Suivi** | Génération de réponses, actions correctives et suivi en temps réel | ResolutionGeneratorAgent, CaseManagerAgent |

## 🔄 3. Workflow Détaillé par Sous-module

### 🟦 1. Collection & Classification

#### 1️⃣ Collecter la Réclamation
- **Agent** : `InputParserAgent`
- **Rôle** : Parser et extraire les données structurées des soumissions de réclamations (web, email, portail)
- **Entrée** : Message utilisateur, pièce jointe (PDF/photo), ID membre, canal d'entrée
- **Sortie** : Données structurées (nom membre, CIN, message, canal), création automatique de ticket, horodatage, lien CRM, accusé de réception instantané

#### 2️⃣ Classifier la Réclamation
- **Agent** : `NLPClassifierAgent`
- **Rôle** : Identifier la catégorie de réclamation via le traitement du langage naturel (NLP)
- **Entrée** : Texte libre du membre ("ma pension n'a pas été payée", "changement RIB non pris en compte")
- **Sortie** : Type de réclamation (paiement, affiliation, contribution, décès, technique), probabilité (%), tag associé
- **Multilingue** : Français, Arabe, Anglais, Amazigh

### 🟩 2. Analyse & Priorisation

#### 3️⃣ Prioriser
- **Agent** : `PriorityScoringAgent`
- **Rôle** : Évaluer l'urgence de la réclamation et déterminer le délai de réponse prioritaire
- **Entrée** : Type de réclamation, ancienneté du dossier, profil membre, mentions d'urgence ("urgent", "non payé depuis 2 mois")
- **Sortie** : Score de priorité (1-5), échéance recommandée (24h, 48h, 5 jours), alerte si réclamation critique

#### 4️⃣ Vérification de Conformité
- **Agent** : `ComplianceCheckerBot`
- **Rôle** : Vérifier la conformité des délais et procédures avec les exigences ACAPS et les normes internes CIMR
- **Entrée** : Temps de traitement, statut du dossier, SLA interne, indicateurs réglementaires
- **Sortie** : Rapport de conformité, alerte de dépassement SLA, recommandation corrective automatique

### 🟨 3. Résolution & Suivi

#### 5️⃣ Brouillon de Résolution
- **Agent** : `ResolutionGeneratorAgent`
- **Rôle** : Proposer ou générer automatiquement des réponses personnalisées selon le type de réclamation
- **Entrée** : Type de dossier, informations membre, historique des réclamations, base de réponses validée
- **Sortie** : Texte de réponse prêt à envoyer, actions internes suggérées (ex: "vérifier le paiement", "contacter le service financier")

#### 6️⃣ Suivi de Cas
- **Agent** : `CaseManagerAgent`
- **Rôle** : Suivre l'évolution de la réclamation jusqu'à la clôture et notifier les membres
- **Entrée** : ID ticket, statut de traitement, utilisateur assigné, interactions précédentes
- **Sortie** : Statut mis à jour ("En cours", "Résolu", "Escalade"), notifications envoyées, rapport de clôture

## 📊 4. Fonctionnalités Clés du Module

✅ **Portail Membre** : Interface Streamlit pour la soumission de réclamations avec support multilingue  
✅ **Tableau de Bord Agent** : Dashboard en temps réel pour les agents internes avec filtres et statistiques  
✅ **Traitement automatique** des pièces jointes et documents justificatifs  
✅ **Classification NLP multilingue** (Français, Arabe, Anglais)  
✅ **Système intelligent de scoring d'urgence** (niveaux de priorité 1-5)  
✅ **Génération automatique de réponses** avec brouillons personnalisés  
✅ **Persistance complète des données** dans Airtable (18 champs gérés par IA)  
✅ **Canal web** entièrement fonctionnel (portée v1)  

## 📈 5. Bénéfices Concrets pour CIMR

| Objectif | Impact |
|----------|--------|
| **Réduction des délais de traitement** | Jusqu'à -70% pour les réclamations simples |
| **Amélioration de la satisfaction des membres** | Réponses automatiques + suivi proactif |
| **Conformité renforcée** | Respect systématique des échéances ACAPS |
| **Efficacité interne accrue** | Moins d'erreurs humaines, gestion centralisée des tickets |
| **Gestion stratégique** | Indicateurs de performance et de qualité en temps réel |

## 🗃️ 6. Schéma Airtable

| Champ | Type | Description | Agent Rempli |
|-------|------|-------------|--------------|
| **Ticket ID** | Numéro automatique | Identifiant unique de la réclamation | Système |
| **Member Name** | Texte | Nom du membre | InputParserAgent |
| **CIN / Adhérent ID** | Texte | CIN ou ID membre | InputParserAgent |
| **Channel** | Sélection unique | Web (portée v1) | InputParserAgent |
| **Message** | Texte long | Réclamation originale | InputParserAgent |
| **Attachment URL** | URL | Lien du fichier uploadé | InputParserAgent |
| **Category** | Sélection unique | Paiement / Affiliation / Contribution / Décès / Technique | NLPClassifierAgent |
| **Confidence** | Nombre | Confiance de classification IA (0.0-1.0) | NLPClassifierAgent |
| **Priority** | Nombre | Score d'urgence 1-5 | PriorityScoringAgent |
| **SLA Hours** | Nombre | Échéance SLA en heures | PriorityScoringAgent |
| **Compliance Status** | Sélection unique | Vert / Jaune / Rouge | ComplianceCheckerBot |
| **Compliance Score** | Nombre | Score de conformité (0.0-1.0) | ComplianceCheckerBot |
| **DraftResponse** | Texte long | Réponse professionnelle générée par IA | ResolutionGeneratorAgent |
| **Response Quality Score** | Nombre | Qualité de la réponse (0.0-1.0) | ResolutionGeneratorAgent |
| **Response Language** | Sélection unique | Français / Arabe / Anglais | ResolutionGeneratorAgent |
| **Status** | Sélection unique | Nouveau / En cours / Résolu | CaseManagerAgent |
| **Case Status** | Sélection unique | Nouveau / En cours / Résolu / Escalade | CaseManagerAgent |
| **Requires Attention** | Case à cocher | Nécessite une attention immédiate | CaseManagerAgent |
| **Assigned Agent** | Texte | Assignation d'agent interne | CaseManagerAgent |
| **Created At** | Horodatage | Horodatage de création | Système |
| **Last Updated** | Horodatage | Horodatage de dernière modification | Système |

## 🤖 7. Orchestration des Agents Agno

Workflow complet en 7 étapes avec sorties structurées et persistance des données.

| Agent | Rôle | Entrée | Sortie |
|-------|------|--------|--------|
| **InputParserAgent** | Parser l'entrée non structurée en données structurées | Texte de réclamation en langage naturel | Données de réclamation structurées (membre, CIN, message) |
| **NLPClassifierAgent** | Classification NLP multilingue des réclamations | Texte du message de réclamation | Catégorie, score de confiance, raisonnement |
| **PriorityScoringAgent** | Évaluer l'urgence et le délai de réponse | Catégorie, message, contexte | Score de priorité (1-5), heures SLA, drapeau d'escalade |
| **ComplianceCheckerBot** | Vérifier la conformité aux normes ACAPS et CIMR | Priorité, SLA, horodatages | Statut de conformité, score, temps restant |
| **ResolutionGeneratorAgent** | Générer des réponses personnalisées | Informations membre, catégorie, priorité | Réponse professionnelle, score de qualité, langue |
| **CaseManagerAgent** | Suivre et clôturer les réclamations | Données complètes de la réclamation | Mises à jour de statut, drapeaux d'attention, assignation d'agent |

### **Étapes du Workflow :**
1. **Parser l'Entrée** → Extraire les données structurées du langage naturel
2. **Créer la Réclamation** → Créer un enregistrement Airtable
3. **Classifier** → Assignation de catégorie alimentée par IA
4. **Prioriser** → Scoring d'urgence et assignation SLA
5. **Vérification de Conformité** → Surveillance de la conformité ACAPS
6. **Générer la Réponse** → Réponse professionnelle multilingue
7. **Gestion de Cas** → Suivi de statut et assignation

## 🎨 8. Recommandations UI/UX

### A. Portail Membre (Streamlit)
- **Champs du formulaire** : Nom, CIN/ID membre, description détaillée de la réclamation
- **Design minimaliste professionnel** : Interface française professionnelle
- **Persistance du formulaire** : Les données restent visibles après soumission
- **Confirmation de succès** : ID ticket affiché avec prochaines étapes
- À la soumission, déclenche le workflow IA complet en 7 étapes

### B. Tableau de Bord Agent (Streamlit)
- **Panneau de statistiques** : Total réclamations, nécessite attention, en cours, résolues
- **Filtres avancés** : Menu déroulant statut, sélection plage de dates
- **Tableau interactif** : Triable par date, badges de priorité colorés
- **Vue détaillée de réclamation** : Tous les 18 champs gérés par IA visibles
- **Mises à jour en temps réel** : Données triées par date (plus récentes en premier)
- **Style professionnel** : Interface minimaliste, propre, entièrement en français

## 🔌 9. Endpoints API (Python / FastAPI)

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/claims/` | Soumettre une nouvelle réclamation (déclenche le workflow complet en 7 étapes) |
| `GET` | `/api/claims/{id}` | Obtenir les détails d'une réclamation spécifique |
| `GET` | `/api/claims/` | Lister les réclamations avec filtrage optionnel |
| `GET` | `/health` | Endpoint de vérification de santé |
| `GET` | `/test-airtable` | Tester la connexion Airtable |

## ✅ 10. Critères de Succès pour V1

- **Flux bout en bout** du formulaire → classification → brouillon de résolution → mise à jour de statut
- **Airtable agit comme source unique de vérité** avec 100% de persistance des données
- **Intervention manuelle minimale** - workflow entièrement automatisé
- **Agents modulaires** (6 agents + orchestration de workflow) prêts pour l'expansion v2
- **Couverture de champ 100%** - Tous les 18 champs de données remplis par les agents IA
- **Prêt pour la production** - Code propre, optimisé, documenté

## 🛠️ 11. Plan d'Implémentation Technique

### Phase 1 : Infrastructure Core
1. Configurer le backend FastAPI avec tous les endpoints
2. Configurer l'intégration Airtable avec opérations CRUD complètes
3. Configurer le framework Agno avec structure d'agents complète
4. Créer une documentation API complète

### Phase 2 : Développement des Agents IA
1. Implémenter `InputParserAgent` pour le parsing d'entrée structurée
2. Développer `NLPClassifierAgent` avec intégration Azure OpenAI
3. Construire `PriorityScoringAgent` avec logique de scoring intelligente
4. Créer `ComplianceCheckerBot` pour la surveillance de conformité ACAPS
5. Implémenter `ResolutionGeneratorAgent` avec génération de réponses multilingues
6. Construire `CaseManagerAgent` pour la gestion complète du cycle de vie des cas

### Phase 3 : Intégration & Tests
1. Connecter tous les agents dans le workflow Agno (processus en 7 étapes)
2. Tester le traitement de réclamation bout en bout avec taux de succès de 100%
3. Implémenter la gestion d'erreurs complète et le logging
4. Ajouter les sorties structurées et la persistance des données

### Phase 4 : Production Ready
1. Nettoyer et optimiser le codebase
2. Supprimer les fichiers et fonctions inutiles
3. Créer une suite de tests complète
4. Compléter la documentation et le statut du projet

## 📋 12. Dépendances & Exigences

### Packages Python
```
fastapi>=0.100.0
uvicorn[standard]>=0.24.0
agno>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
openai>=1.3.7
airtable-python-wrapper>=0.15.3
requests>=2.31.0
streamlit>=1.28.0
pandas>=2.0.0
loguru>=0.7.2
```

### Services Externes
- Compte Airtable avec clé API
- Clé API Azure OpenAI et configuration
- Configuration d'environnement (template .env)

## 🔧 13. Configuration Environnement

```env
# Paramètres Application
APP_NAME=CIMR Claims Automation v1
APP_VERSION=1.0.0
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Configuration Airtable
AIRTABLE_API_KEY=votre_cle_api_airtable
AIRTABLE_BASE_ID=votre_base_id
AIRTABLE_TABLE_NAME=claims

# Configuration Azure OpenAI
AZURE_OPENAI_DEPLOYMENT_NAME=nom_de_deploiement
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com/
AZURE_OPENAI_API_KEY=votre_cle_api_azure_openai

# Configuration CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8501"]
```

**Note** : Canal web uniquement pour v1. Intégrations WhatsApp/Email prévues pour v2+.

## 📊 14. Surveillance & Analytiques (Futur v2)

- Métriques de traitement des réclamations
- Analytiques de performance des agents
- Suivi du temps de réponse
- Scores de satisfaction client
- Analyse de distribution des catégories

## 🚀 15. Considérations de Déploiement

- Containerisation Docker pour déploiement facile
- Configuration spécifique à l'environnement
- Stratégies de sauvegarde de base de données
- Limitation du débit API
- Bonnes pratiques de sécurité (gestion des clés API)

---

## 📝 Notes

Ce document de référence sert de spécification technique complète pour l'Automatisation des Réclamations CIMR v1. Tous les composants sont conçus pour être modulaires et évolutifs pour des améliorations futures.

**Dernière mise à jour** : 27 octobre 2025  
**Version** : 1.0.0  
**Statut** : Prêt pour la Production

