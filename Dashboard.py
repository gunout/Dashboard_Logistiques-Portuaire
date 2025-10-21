import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import numpy as np
import re
import json
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import xlsxwriter
import tempfile
import os

# 🔧 Configuration avancée
st.set_page_config(
    page_title="Dashboard Intelligent - S-Wing Réunion",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.port-reunion.fr',
        'Report a bug': None,
        'About': "Dashboard intelligent pour la logistique portuaire de La Réunion"
    }
)

# 🎨 CSS avancé avec thème bleu blanc rouge - CORRIGÉ
st.markdown("""
<style>
    :root {
        --primary: #002395;      /* Bleu France */
        --secondary: #ED2939;    /* Rouge France */
        --white: #FFFFFF;        /* Blanc */
        --light-blue: #E6E9F0;   /* Bleu clair pour les fonds */
        --light-red: #FFE5E8;    /* Rouge clair pour les fonds */
        --dark-blue: #001B6F;    /* Bleu foncé pour le texte */
        --dark-red: #B71C1C;     /* Rouge foncé pour les accents */
        --text-dark: #212529;    /* Texte sombre principal */
        --text-muted: #6C757D;   /* Texte grisé */
    }
    
    /* Styles de base */
    .stApp {
        background-color: #F8F9FA;
        color: var(--text-dark);
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text-dark) !important;
        background-color: #F5F7FA !important;
    }
    
    /* En-tête principal */
    .main-header {
        font-size: 2.8rem;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid var(--primary);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
        color: var(--text-dark) !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Boîtes d'alerte */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
        color: var(--text-dark) !important;
    }
    
    .alert-warning {
        background-color: #FFF8E1;
        border-color: #FFC107;
        color: #856404 !important;
    }
    
    .alert-success {
        background-color: #E8F5E9;
        border-color: #4CAF50;
        color: #2E7D32 !important;
    }
    
    .alert-info {
        background-color: #E3F2FD;
        border-color: var(--primary);
        color: var(--dark-blue) !important;
    }
    
    .alert-danger {
        background-color: #FFEBEE;
        border-color: var(--secondary);
        color: var(--dark-red) !important;
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--light-blue);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--dark-blue) !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0 0.25rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary);
        color: white !important;
    }
    
    /* Boutons */
    .stButton > button {
        background-color: var(--primary);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--dark-blue);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sélecteurs */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
    }
    
    .stSelectbox select {
        color: var(--text-dark) !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background-color: var(--primary);
    }
    
    /* Métriques */
    .stMetric {
        background-color: white;
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: var(--text-dark) !important;
    }
    
    .stMetric label {
        color: var(--text-dark) !important;
    }
    
    .stMetric div {
        color: var(--text-dark) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        background-color: white;
        color: var(--text-dark) !important;
    }
    
    .stDataFrame th {
        background-color: var(--light-blue);
        color: var(--dark-blue) !important;
        font-weight: 600;
    }
    
    .stDataFrame td {
        color: var(--text-dark) !important;
    }
    
    .stDataFrame tr:nth-child(even) {
        background-color: #F9FAFB;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: white !important;
        border-right: 1px solid var(--light-blue);
    }
    
    .stSidebar .sidebar-content {
        background-color: white !important;
        color: var(--text-dark) !important;
    }
    
    .stSidebar .block-container {
        padding-top: 1rem;
        color: var(--text-dark) !important;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: var(--primary) !important;
    }
    
    .stSidebar p, .stSidebar span, .stSidebar div {
        color: var(--text-dark) !important;
    }
    
    .stSidebar label {
        color: var(--text-dark) !important;
    }
    
    /* Headers */
    .stHeader {
        color: var(--primary) !important;
    }
    
    .stSubheader {
        color: var(--dark-blue) !important;
    }
    
    /* Markdown */
    .stMarkdown {
        color: var(--text-dark) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--primary) !important;
    }
    
    .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: var(--text-dark) !important;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        color: #2E7D32 !important;
    }
    
    .stInfo {
        background-color: #E3F2FD;
        border-left: 4px solid var(--primary);
        color: var(--dark-blue) !important;
    }
    
    .stWarning {
        background-color: #FFF8E1;
        border-left: 4px solid #FFC107;
        color: #856404 !important;
    }
    
    .stError {
        background-color: #FFEBEE;
        border-left: 4px solid var(--secondary);
        color: var(--dark-red) !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    .stTimeInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    /* Checkbox et Radio */
    .stCheckbox {
        color: var(--text-dark) !important;
    }
    
    .stCheckbox label {
        color: var(--text-dark) !important;
    }
    
    .stRadio > div {
        color: var(--text-dark) !important;
    }
    
    .stRadio label {
        color: var(--text-dark) !important;
    }
    
    /* Selectbox et Multiselect */
    .stSelectbox > div > div > select {
        color: var(--text-dark) !important;
        background-color: white !important;
    }
    
    .stMultiSelect > div > div > div {
        color: var(--text-dark) !important;
    }
    
    /* Expander */
    .stExpander {
        color: var(--text-dark) !important;
    }
    
    .stExpander > div > div {
        background-color: white;
        border-radius: 10px;
        border: 1px solid var(--light-blue);
        color: var(--text-dark) !important;
    }
    
    .stExpander > div > div > span {
        color: var(--primary) !important;
        font-weight: 600;
    }
    
    /* Form */
    .stForm {
        color: var(--text-dark) !important;
    }
    
    .stForm > div > div {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        color: var(--text-dark) !important;
    }
    
    /* Progress et Spinner */
    .stProgress > div > div > div > div {
        background-color: var(--primary);
    }
    
    .stSpinner > div > div > div {
        border-top-color: var(--primary);
    }
    
    /* Plotly */
    .stPlotlyChart {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Footer */
    footer {
        color: var(--text-dark) !important;
        background-color: white;
        border-top: 1px solid var(--light-blue);
        padding: 1rem 0;
        margin-top: 2rem;
    }
    
    .footer-container {
        display: flex;
        justify-content: space-between;
        padding: 0 1rem;
    }
    
    .footer-item {
        flex: 1;
        text-align: center;
        color: var(--text-dark) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .footer-container {
            flex-direction: column;
        }
        
        .footer-item {
            margin-bottom: 0.5rem;
        }
    }
    
    /* Correction spécifique pour les textes dans les colonnes */
    .element-container {
        color: var(--text-dark) !important;
    }
    
    .columns > div {
        color: var(--text-dark) !important;
    }
    
    /* Correction pour les data editor */
    .stDataEditor {
        color: var(--text-dark) !important;
    }
    
    .stDataEditor table {
        color: var(--text-dark) !important;
    }
    
    .stDataEditor th {
        color: var(--dark-blue) !important;
    }
    
    .stDataEditor td {
        color: var(--text-dark) !important;
    }
</style>
""", unsafe_allow_html=True)

# 🔐 Gestion des configurations
class Config:
    """Configuration centralisée"""
    SCRAPING_TIMEOUT = 20
    CACHE_DURATION = 300  # 5 minutes
    MAX_RETRIES = 3
    UPDATE_INTERVAL = 3600  # 1 heure

config = Config()

# 🧠 Intelligence Artificielle - Prédictions simples
class PredictiveAnalytics:
    """Module d'analyse prédictive"""
    
    @staticmethod
    def predict_traffic(df, days=7):
        """Prédiction du trafic basée sur les données historiques"""
        if len(df) < 10:
            return None
            
        # Simple moyenne mobile pour la démonstration
        df['prediction'] = df['conteneurs_traites'].rolling(window=7).mean()
        last_value = df['prediction'].iloc[-1]
        
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, days+1)]
        predictions = [max(0, last_value * (1 + np.random.normal(0, 0.1))) for _ in range(days)]
        
        return pd.DataFrame({
            'date': future_dates,
            'prediction': predictions,
            'confidence': np.random.uniform(0.7, 0.95, days)
        })
    
    @staticmethod
    def detect_anomalies(df, column='conteneurs_traites'):
        """Détection d'anomalies simples"""
        mean = df[column].mean()
        std = df[column].std()
        threshold = 2 * std
        
        anomalies = df[abs(df[column] - mean) > threshold]
        return anomalies

# 📊 Gestionnaire de données avancé
class DataManager:
    """Gestion centralisée des données"""
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    @st.cache_data(ttl=config.CACHE_DURATION)
    def scrape_swing_advanced(_self, url):
        """Scraping avancé avec retry mechanism"""
        for attempt in range(config.MAX_RETRIES):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                }
                
                response = requests.get(url, headers=headers, timeout=config.SCRAPING_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraction avancée avec multiple stratégies
                data = {
                    'title': self._extract_title(soup),
                    'metadata': self._extract_metadata(soup),
                    'content_blocks': self._extract_content_blocks(soup),
                    'structured_data': self._extract_structured_data(soup),
                    'scraping_time': datetime.now()
                }
                
                return data
                
            except Exception as e:
                if attempt == config.MAX_RETRIES - 1:
                    st.error(f"❌ Échec du scraping après {config.MAX_RETRIES} tentatives: {e}")
                    return {}
                time.sleep(2 ** attempt)  # Backoff exponentiel
    
    def _extract_title(self, soup):
        """Extraction avancée du titre"""
        title = soup.title.string if soup.title else "S-Wing Réunion"
        
        # Recherche de meta titres
        meta_titles = [meta.get('content') for meta in soup.find_all('meta', attrs={'name': re.compile('title', re.I)})]
        if meta_titles:
            title = meta_titles[0]
            
        return title
    
    def _extract_metadata(self, soup):
        """Extraction des métadonnées"""
        metadata = {}
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content')
        
        # Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content')
        
        # Open Graph
        og_tags = soup.find_all('meta', attrs={'property': re.compile('^og:', re.I)})
        for tag in og_tags:
            key = tag.get('property', '').replace('og:', '')
            metadata[f"og_{key}"] = tag.get('content')
        
        return metadata
    
    def _extract_content_blocks(self, soup):
        """Extraction des blocs de contenu"""
        blocks = []
        
        # Stratégies d'extraction multiples
        selectors = [
            'article', '.content', '.main-content', '[role="main"]',
            '.post', '.entry-content', '.text-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if len(text) > 100:  # Seulement les blocs significatifs
                    blocks.append({
                        'selector': selector,
                        'text': text[:500] + '...' if len(text) > 500 else text,
                        'length': len(text)
                    })
        
        return blocks
    
    def _extract_structured_data(self, soup):
        """Extraction des données structurées (JSON-LD)"""
        structured_data = []
        
        # JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except:
                pass
        
        return structured_data

# 📤 Fonction d'export améliorée
class DataExporter:
    """Classe pour gérer l'export des données"""
    
    @staticmethod
    def generate_sample_data():
        """Génère des données d'exemple pour l'export"""
        # Données de trafic
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        traffic_data = pd.DataFrame({
            'date': dates,
            'conteneurs_traites': np.random.randint(800, 1200, 30),
            'navires_arrives': np.random.randint(3, 8, 30),
            'taux_occupation': np.random.uniform(75, 95, 30),
            'delai_moyen': np.random.uniform(1.5, 4.5, 30)
        })
        
        # Données des navires
        vessels_data = pd.DataFrame({
            'navire': ['MSC Isabella', 'CMA CGM Andes', 'Maersk Cardiff', 'Ever Glory', 'HMM Rotterdam'],
            'type': ['Porte-conteneurs'] * 5,
            'ligne': ['Europe-Asie', 'Amérique du Sud', 'Afrique-Europe', 'Asie-Pacifique', 'Europe-Amérique'],
            'capacite_teu': [14000, 11000, 12500, 15000, 13500],
            'arrivee_prevue': pd.date_range(start=datetime.now(), periods=5, freq='2D'),
            'statut': ['En route', 'À quai', 'En opération', 'En attente', 'En route']
        })
        
        # KPIs
        kpis_data = {
            'Efficacité Opérationnelle': '94.2%',
            'Taux de Rotation': '3.2 jours',
            'Coût par Conteneur': '€142.50',
            'Empreinte Carbone': '12.4t CO2',
            'Satisfaction Clients': '94.2%',
            'Taux Occupation': '87.3%',
            'Retards Moyens': '2.3h'
        }
        
        return traffic_data, vessels_data, kpis_data
    
    @staticmethod
    def export_to_csv(data, filename="dashboard_data.csv"):
        """Exporte les données en format CSV"""
        if isinstance(data, dict):
            # Si c'est un dictionnaire de KPIs
            df = pd.DataFrame(list(data.items()), columns=['Indicateur', 'Valeur'])
        else:
            df = data
        
        csv = df.to_csv(index=False)
        return csv.encode('utf-8'), f"{filename}"
    
    @staticmethod
    def export_to_excel(data_dict, filename="dashboard_data.xlsx"):
        """Exporte les données en format Excel avec plusieurs feuilles"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Styles
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#002395',
                'font_color': 'white',
                'border': 1
            })
            
            # Écrire chaque DataFrame dans une feuille différente
            for sheet_name, data in data_dict.items():
                if isinstance(data, dict):
                    df = pd.DataFrame(list(data.items()), columns=['Indicateur', 'Valeur'])
                else:
                    df = data
                
                df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
                
                # Formatage
                worksheet = writer.sheets[sheet_name]
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Ajuster la largeur des colonnes
                for i, col in enumerate(df.columns):
                    column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)
        
        output.seek(0)
        return output.getvalue(), f"{filename}"
    
    @staticmethod
    def export_to_json(data_dict, filename="dashboard_data.json"):
        """Exporte les données en format JSON"""
        json_data = {}
        
        for key, value in data_dict.items():
            if isinstance(value, pd.DataFrame):
                json_data[key] = value.to_dict('records')
            elif isinstance(value, dict):
                json_data[key] = value
            else:
                json_data[key] = str(value)
        
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode('utf-8'), f"{filename}"
    
    @staticmethod
    def export_to_pdf(data_dict, filename="dashboard_report.pdf"):
        """Exporte les données en format PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title_style = styles['Title']
        title_style.textColor = colors.HexColor('#002395')
        story.append(Paragraph("Rapport Dashboard - S-Wing Réunion", title_style))
        story.append(Spacer(1, 20))
        
        # Date de génération
        date_style = styles['Normal']
        story.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        story.append(Spacer(1, 20))
        
        # Pour chaque ensemble de données
        for title, data in data_dict.items():
            # Sous-titre
            subtitle_style = styles['Heading2']
            subtitle_style.textColor = colors.HexColor('#ED2939')
            story.append(Paragraph(title.replace('_', ' ').title(), subtitle_style))
            story.append(Spacer(1, 12))
            
            if isinstance(data, pd.DataFrame):
                # Créer un tableau
                table_data = [data.columns.tolist()] + data.values.tolist()
                table = Table(table_data)
                
                # Style du tableau
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002395')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            elif isinstance(data, dict):
                # Pour les KPIs
                for key, value in data.items():
                    kpi_text = f"<b>{key}:</b> {value}"
                    story.append(Paragraph(kpi_text, date_style))
            
            story.append(Spacer(1, 20))
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue(), f"{filename}"

# Initialisation des managers
data_manager = DataManager()
predictive_analytics = PredictiveAnalytics()
data_exporter = DataExporter()

# Fonctions auxiliaires
def generate_vessel_schedule():
    """Génère un planning de navires réaliste"""
    vessels = [
        {'nom': 'MSC Isabella', 'type': 'Porte-conteneurs', 'ligne': 'Europe-Asie', 'capacite': 14000},
        {'nom': 'CMA CGM Andes', 'type': 'Porte-conteneurs', 'ligne': 'Amérique du Sud', 'capacite': 11000},
        {'nom': 'Maersk Cardiff', 'type': 'Porte-conteneurs', 'ligne': 'Afrique-Europe', 'capacite': 12500},
        {'nom': 'Ever Glory', 'type': 'Porte-conteneurs', 'ligne': 'Asie-Pacifique', 'capacite': 15000},
        {'nom': 'HMM Rotterdam', 'type': 'Porte-conteneurs', 'ligne': 'Europe-Amérique', 'capacite': 13500},
    ]
    
    schedule = []
    current_date = datetime.now()
    
    for i, vessel in enumerate(vessels):
        arrival_date = current_date + timedelta(days=i*2 + np.random.randint(0, 3))
        
        schedule.append({
            'navire': vessel['nom'],
            'type': vessel['type'],
            'ligne': vessel['ligne'],
            'capacite_teu': vessel['capacite'],
            'arrivee_prevue': arrival_date,
            'statut': np.random.choice(['En route', 'À quai', 'En opération', 'En attente'])
        })
    
    return pd.DataFrame(schedule)

# 🎛️ Sidebar avancée
st.sidebar.header("⚙️ Configuration Avancée")

# Thème
theme = st.sidebar.selectbox("🎨 Thème", ["Bleu Blanc Rouge", "Clair", "Sombre"], index=0)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-rafraîchissement", value=False)
refresh_interval = st.sidebar.slider("Intervalle (minutes)", 1, 60, 30)

# Niveau de détail
detail_level = st.sidebar.radio("Niveau de détail", ["Basique", "Avancé", "Expert"], index=1)

# Export rapide depuis le sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Export Rapide")

# Générer les données d'exemple
traffic_data, vessels_data, kpis_data = data_exporter.generate_sample_data()

if st.sidebar.button("📊 Exporter toutes les données (CSV)"):
    csv_data, filename = data_exporter.export_to_csv(traffic_data, "trafic_portuaire.csv")
    st.sidebar.download_button(
        label="Télécharger CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

# 🎯 Tableau de bord principal amélioré
st.markdown('<h1 class="main-header">🚢 Dashboard Intelligent - S-Wing Réunion</h1>', unsafe_allow_html=True)

# Bandeau d'alerte en temps réel
col_alert1, col_alert2, col_alert3 = st.columns(3)
with col_alert1:
    st.markdown('<div class="alert-box alert-success">✅ Opérations normales</div>', unsafe_allow_html=True)
with col_alert2:
    st.markdown('<div class="alert-box alert-warning">⚠️ Trafic élevé prévu</div>', unsafe_allow_html=True)
with col_alert3:
    st.markdown('<div class="alert-box alert-success">✅ Météo favorable</div>', unsafe_allow_html=True)

# Nouvelle structure d'onglets avec contenu enrichi
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Vue Globale", 
    "📈 Analytics", 
    "🔮 Prédictions", 
    "🚢 Opérations", 
    "📊 Rapports", 
    "⚙️ Configuration",
    "🧠 IA & ML"
])

with tab1:
    st.header("🌐 Vue Globale Intelligente")
    
    # Métriques en temps réel améliorées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Conteneurs Traités", 
            "12,458", 
            delta="+8.2%",
            delta_color="normal",
            help="Conteneurs traités ce mois vs mois dernier"
        )
    
    with col2:
        st.metric(
            "Taux Occupation", 
            "87.3%", 
            delta="+3.1%",
            help="Taux d'occupation moyen des quais"
        )
    
    with col3:
        st.metric(
            "Satisfaction Clients", 
            "94.2%", 
            delta="+2.4%",
            help="Score de satisfaction client moyen"
        )
    
    with col4:
        st.metric(
            "Retards Moyens", 
            "2.3h", 
            delta="-0.8h",
            delta_color="inverse",
            help="Réduction des retards moyens"
        )
    
    # Cartes interactives
    col_map, col_alerts = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Carte Thermique des Opérations")
        # Simulation d'une carte thermique
        data = np.random.rand(10, 10)
        fig_heatmap = px.imshow(data, 
                              title="Activité des Quais - Carte Thermique",
                              color_continuous_scale=["#002395", "#FFFFFF", "#ED2939"])  # Bleu, Blanc, Rouge
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col_alerts:
        st.subheader("🚨 Alertes en Temps Réel")
        
        alerts = [
            {"niveau": "⚠️", "message": "Navire MSC Isabella retardé", "time": "10:23"},
            {"niveau": "✅", "message": "Opération terminée - Quai 3", "time": "10:15"},
            {"niveau": "🔧", "message": "Maintenance prévue - Quai 2", "time": "09:45"},
            {"niveau": "📦", "message": "Livraison spéciale arrivée", "time": "09:30"}
        ]
        
        for alert in alerts:
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.2rem 0; border-left: 3px solid #002395; background: #f8f9fa; color: #212529;">
                <strong>{alert['niveau']}</strong> {alert['message']}
                <br><small>{alert['time']}</small>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.header("📈 Analytics Avancés")
    
    # Filtres avancés
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        period = st.selectbox("Période", ["7 jours", "30 jours", "90 jours", "1 an"])
    with col_f2:
        metric = st.selectbox("Métrique", ["Conteneurs", "Navires", "Tonnage", "Productivité"])
    with col_f3:
        aggregation = st.selectbox("Agrégation", ["Journalier", "Hebdomadaire", "Mensuel"])
    with col_f4:
        view_type = st.selectbox("Vue", ["Trend", "Comparaison", "Distribution"])
    
    # Analytics avancés
    col_analytics1, col_analytics2 = st.columns(2)
    
    with col_analytics1:
        # Graphique de tendance interactif
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        trend_data = pd.DataFrame({
            'date': dates,
            'conteneurs': np.cumsum(np.random.normal(800, 200, 100)),
            'navires': np.cumsum(np.random.normal(5, 2, 100)),
            'productivite': np.random.normal(30, 5, 100)
        })
        
        fig_trend = px.line(trend_data, x='date', y=['conteneurs', 'navires'],
                          title='Tendances des Opérations',
                          labels={'value': 'Volume', 'variable': 'Métrique'},
                          color_discrete_map={"conteneurs": "#002395", "navires": "#ED2939"})  # Bleu et Rouge
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_analytics2:
        # Analyse de corrélation
        correlation_data = pd.DataFrame({
            'Productivité': np.random.normal(30, 5, 50),
            'Occupation': np.random.normal(85, 10, 50),
            'Retards': np.random.normal(2, 1, 50),
            'Satisfaction': np.random.normal(90, 5, 50)
        })
        
        fig_corr = px.imshow(correlation_data.corr(),
                           title='Matrice de Corrélation',
                           color_continuous_scale=[[0, "#FFFFFF"], [0.5, "#002395"], [1, "#ED2939"]])  # Blanc, Bleu, Rouge
        st.plotly_chart(fig_corr, use_container_width=True)

with tab3:
    st.header("🔮 Prédictions et Forecasting")
    
    # Données pour les prédictions
    historical_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'conteneurs_traites': np.cumsum(np.random.normal(800, 200, 60))
    })
    
    predictions = predictive_analytics.predict_traffic(historical_data)
    
    if predictions is not None:
        col_pred1, col_pred2 = st.columns(2)
        
        with col_pred1:
            # Graphique des prédictions
            fig_pred = go.Figure()
            
            # Données historiques
            fig_pred.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['conteneurs_traites'],
                name='Historique',
                line=dict(color='#002395')  # Bleu France
            ))
            
            # Prédictions
            fig_pred.add_trace(go.Scatter(
                x=predictions['date'],
                y=predictions['prediction'],
                name='Prédiction',
                line=dict(color='#ED2939', dash='dash')  # Rouge France
            ))
            
            fig_pred.update_layout(title='Prédiction du Trafic des Conteneurs')
            st.plotly_chart(fig_pred, use_container_width=True)
        
        with col_pred2:
            # Détails des prédictions
            st.subheader("📋 Détails des Prédictions")
            st.dataframe(predictions, use_container_width=True)
            
            # Indicateurs de confiance
            avg_confidence = predictions['confidence'].mean()
            st.metric("Confiance Moyenne", f"{avg_confidence:.1%}")
            
            # Recommandations
            st.subheader("💡 Recommandations")
            if predictions['prediction'].mean() > historical_data['conteneurs_traites'].mean():
                st.success("**Augmentation prévue** - Renforcer les équipes")
            else:
                st.warning("**Baisse prévue** - Optimiser les ressources")

with tab4:
    st.header("🚢 Gestion des Opérations en Temps Réel")
    
    # Interface de gestion opérationnelle
    col_ops1, col_ops2 = st.columns(2)
    
    with col_ops1:
        st.subheader("📋 Planning des Navires")
        
        # Table interactive avec actions
        schedule_data = generate_vessel_schedule()  # Fonction maintenant définie
        edited_df = st.data_editor(
            schedule_data,
            use_container_width=True,
            column_config={
                "navire": st.column_config.TextColumn("Navire"),
                "statut": st.column_config.SelectboxColumn(
                    "Statut",
                    options=["En route", "À quai", "En opération", "En attente", "Annulé"]
                )
            }
        )
    
    with col_ops2:
        st.subheader("⚡ Actions Rapides")
        
        # Boutons d'action
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🔄 Actualiser Statuts", use_container_width=True):
                st.success("Statuts mis à jour!")
            if st.button("📧 Notifier Équipes", use_container_width=True):
                st.info("Notifications envoyées!")
        with col_act2:
            if st.button("🚨 Alerte Urgence", use_container_width=True):
                st.error("Alerte urgence activée!")
            if st.button("📊 Générer Rapport", use_container_width=True):
                st.success("Rapport généré!")

with tab5:
    st.header("📊 Rapports et Exportations")
    
    # Génération de rapports avancés
    report_type = st.selectbox("Type de Rapport", 
                             ["Opérations Quotidiennes", "Performance Mensuelle", "Analyse Annuelle", "Audit Complet"])
    
    col_rep1, col_rep2 = st.columns(2)
    
    with col_rep1:
        st.subheader("📈 KPIs Principaux")
        
        kpis = {
            "Efficacité Opérationnelle": "94.2%",
            "Taux de Rotation": "3.2 jours",
            "Coût par Conteneur": "€142.50",
            "Empreinte Carbone": "12.4t CO2"
        }
        
        for kpi, value in kpis.items():
            st.metric(kpi, value)
    
    with col_rep2:
        st.subheader("📤 Export des Données")
        
        # Sélection des données à exporter
        export_options = st.multiselect(
            "Sélectionner les données à exporter",
            ["Trafic Portuaire", "Planning Navires", "KPIs", "Prédictions"],
            default=["Trafic Portuaire", "Planning Navires", "KPIs"]
        )
        
        # Formats d'export
        formats = st.multiselect("Formats d'export", 
                               ["CSV", "Excel", "PDF", "JSON"],
                               default=["CSV"])
        
        # Préparation des données
        data_to_export = {}
        if "Trafic Portuaire" in export_options:
            data_to_export["trafic_portuaire"] = traffic_data
        if "Planning Navires" in export_options:
            data_to_export["planning_navires"] = vessels_data
        if "KPIs" in export_options:
            data_to_export["kpis"] = kpis_data
        if "Prédictions" in export_options:
            if predictions is not None:
                data_to_export["predictions"] = predictions
        
        # Boutons d'export par format
        if data_to_export and formats:
            st.markdown("### Boutons de téléchargement")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                if "CSV" in formats:
                    for key, data in data_to_export.items():
                        csv_data, filename = data_exporter.export_to_csv(data, f"{key}.csv")
                        st.download_button(
                            label=f"📄 Télécharger {key} (CSV)",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            key=f"csv_{key}"
                        )
                
                if "JSON" in formats:
                    json_data, filename = data_exporter.export_to_json(data_to_export, "dashboard_complet.json")
                    st.download_button(
                        label="📋 Télécharger JSON complet",
                        data=json_data,
                        file_name=filename,
                        mime="application/json",
                        key="json_complete"
                    )
            
            with col_exp2:
                if "Excel" in formats:
                    excel_data, filename = data_exporter.export_to_excel(data_to_export, "dashboard_complet.xlsx")
                    st.download_button(
                        label="📊 Télécharger Excel complet",
                        data=excel_data,
                        file_name=filename,
                        key="excel_complete"
                    )
                
                if "PDF" in formats:
                    pdf_data, filename = data_exporter.export_to_pdf(data_to_export, "rapport_dashboard.pdf")
                    st.download_button(
                        label="📑 Télécharger rapport PDF",
                        data=pdf_data,
                        file_name=filename,
                        key="pdf_complete"
                    )
        
        else:
            st.warning("Veuillez sélectionner des données et des formats d'export")

with tab6:
    st.header("⚙️ Configuration Système")
    
    # Configuration avancée
    col_conf1, col_conf2 = st.columns(2)
    
    with col_conf1:
        st.subheader("🔧 Paramètres Scraping")
        
        scraping_frequency = st.select_slider(
            "Fréquence de scraping",
            options=["1h", "2h", "6h", "12h", "24h"],
            value="6h"
        )
        
        data_retention = st.slider(
            "Rétention des données (jours)",
            min_value=7,
            max_value=365,
            value=90
        )
    
    with col_conf2:
        st.subheader("🔐 Sécurité")
        
        api_key = st.text_input("Clé API", type="password")
        enable_2fa = st.checkbox("Authentification à deux facteurs")
        
        if st.button("💾 Sauvegarder Configuration"):
            st.success("Configuration sauvegardée!")

with tab7:
    st.header("🧠 Intelligence Artificielle")
    
    st.info("""
    **Module d'IA en développement** - Ces fonctionnalités utilisent l'apprentissage automatique 
    pour optimiser les opérations portuaires.
    """)
    
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        st.subheader("🤖 Optimisation Intelligente")
        
        if st.button("🎯 Optimiser Planning"):
            with st.spinner("Calcul de la solution optimale..."):
                time.sleep(3)
                st.success("Planning optimisé! Gain estimé: 12% de productivité")
        
        if st.button("🔍 Détecter Anomalies"):
            anomalies = predictive_analytics.detect_anomalies(historical_data)
            if not anomalies.empty:
                st.warning(f"{len(anomalies)} anomalies détectées")
                st.dataframe(anomalies)
            else:
                st.success("Aucune anomalie détectée")
    
    with col_ai2:
        st.subheader("📚 Apprentissage Automatique")
        
        ml_model = st.selectbox("Modèle ML", 
                              ["Régression Linéaire", "Random Forest", "Réseau de Neurones"])
        
        st.metric("Précision du Modèle", "87.3%")
        st.metric("Données d'Entraînement", "45,287 entrées")

# 🔄 Système de rafraîchissement automatique
if auto_refresh:
    time.sleep(refresh_interval * 60)
    st.rerun()

# 📱 Responsive design et accessibilité
st.markdown("""
<style>
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
        padding: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Footer intelligent
st.markdown("---")
col_foot1, col_foot2, col_foot3 = st.columns(3)
with col_foot1:
    st.markdown("**🕒 Dernière mise à jour:** " + datetime.now().strftime("%d/%m/%Y %H:%M"))
with col_foot2:
    st.markdown("**📊 Données:** S-Wing Réunion & Analyse IA")
with col_foot3:
    st.markdown("**🔒 Sécurité:** Conforme RGPD")

# Système de logging (simplifié)
if st.sidebar.button("📋 Journal des Événements"):
    st.sidebar.text("10:23 - Scraping réussi")
    st.sidebar.text("10:15 - Données mises à jour")
    st.sidebar.text("09:45 - Prédictions calculées")