# Jibarito - Agricultural Intelligence Agent

A bilingual (Spanish/English) chatbot powered by Neo4j Aura Agent that provides agricultural intelligence for the US Caribbean and tropical regions (Puerto Rico, US Virgin Islands, Hawaii, Florida).

## Features

- 🌾 **Crop Production Statistics** - USDA NASS data (2018-2023)
- 🤝 **Companion Planting** - What to grow together
- 🐛 **Pest Management** - Organic solutions for pests and diseases
- 📊 **Growing Information** - Spacing, harvest times, climate requirements
- 🌍 **Regional Comparison** - Compare production across territories
- 🇺🇸 🇵🇷 **Bilingual** - Spanish and English support

## Quick Start

### Local Development

1. **Clone and setup**:
```bash
git clone <repo>
cd jibarito_agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Create local secrets** (from template):
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Then edit `.streamlit/secrets.toml` and add your credentials:
```toml
agent_endpoint = "https://api.neo4j.io/v2beta1/organizations/..."
agent_bearer_token = "your_bearer_token_here"
```

3. **Run the app**:
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

**Note**: `.streamlit/secrets.toml` is gitignored for security. Never commit it.

### Deploy to Streamlit Cloud

**Prerequisites**: Your repo must be public on GitHub

1. **Push this repo to GitHub**:
```bash
git push origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select:
     - GitHub account
     - Repository: `jibarito_agent`
     - Branch: `main`
     - Main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Add secrets** (after deployment starts):
   - Click App menu (⋮) → Settings
   - Go to "Secrets" section
   - Add your secrets in TOML format:
   ```toml
   agent_endpoint = "https://api.neo4j.io/v2beta1/organizations/..."
   agent_bearer_token = "your_bearer_token_here"
   ```
   - Save and app will auto-rerun with secrets

4. **Your app is live!**
   - Share the URL with users
   - App auto-redeploys on git push

## Example Queries

**English**:
- "What crops does Puerto Rico grow?"
- "What can I plant next to tomatoes?"
- "What pests attack plantains?"
- "How do I grow cassava?"
- "Compare mango production between Hawaii and Puerto Rico"

**Spanish**:
- "¿Qué cultivos se producen en Puerto Rico?"
- "¿Qué puedo sembrar junto a los tomates?"
- "¿Qué plagas atacan los plátanos?"
- "¿Cómo cultivo yuca?"
- "Compara la producción de mangos entre Hawái y Puerto Rico"

## Data

- **92,218 agricultural records** from USDA NASS Quick Stats
- **4 territories**: Puerto Rico, US Virgin Islands, Hawaii, Florida
- **3 census years**: 2018, 2022, 2023
- **228 crops** with growing information
- **262 pests** with organic management strategies
- **Companion relationships** from CropGraph API

## Architecture

```
User Query (Streamlit UI)
    ↓
REST API POST to Neo4j Aura Agent
    ↓
Aura Agent (with tools for similarity search + Cypher queries)
    ↓
Neo4j Knowledge Graph (92K+ nodes, 213K+ relationships)
    ↓
Response back to Streamlit
    ↓
Display in Chat Interface
```

## Requirements

See `requirements.txt`:
- streamlit==1.31.0
- requests==2.31.0
- python-dotenv==1.0.1

## License

See LICENSE file

## About

**Jibarito** (ji-bah-REE-to) = Puerto Rican farmer/campesino

Built for the Neo4j Aura Agents Hackathon
