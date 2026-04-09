# 🇮🇳 Yojana AI - Gujarat Government Scheme Assistant

Yojana AI is an intelligent, omnichannel platform designed to bridge the gap between complex government policies and the citizens who need them. It uses advanced RAG (Retrieval-Augmented Generation) to provide instant, accurate, and multilingual information about Gujarat government schemes.

## 🚀 Features
- **Semantic Search**: Find schemes based on your needs (e.g., "schemes for small farmers" or "education loans").
- **Eligibility Checking**: Provide your profile details (age, income, caste, etc.) to see a personalized list of matched schemes.
- **Multilingual Support**: Fully functional in **English**, **Hindi**, and **Gujarati**.
- **Omnichannel Access**: Chat via Web UI, Telegram, or WhatsApp.
- **Voice Integration**: Supports voice input and real-time audio responses.
- **Daily Updates**: Automated cleaning and syncing of new schemes from official government portals.

## 🛠️ Tech Stack
-   **Frontend**: Flask, Tailwind CSS, JavaScript (Vanilla).
-   **AI / RAG**: Mistral AI (LLM & Embeddings), LangChain.
-   **Database**: Supabase (PostgreSQL + pgvector).
-   **Scraping**: Playwright, GitHub Actions.
-   **Communication**: Telegram (python-telegram-bot), WhatsApp (Twilio).
-   **Voice**: Edge-TTS.

## 📁 Project Structure
```text
├── .github/workflows/      # Automated scrapers and sync jobs
├── api/                    # Vercel serverless entry points
├── bot/                    # Telegram integration handler
├── database/               # SQL migrations and DB models
├── frontend/               # Web UI assets and Flask routes
├── rag/                    # AI logic (Intent, Retriever, LLM)
├── scraper/                # Playwright scraping logic
├── utils/                  # TTS, Notifier, and Secret helpers
└── vercel.json             # Deployment configuration
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Supabase Account (with pgvector enabled)
- Mistral AI API Key

### 2. Local Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/viralgohel92/gov-schemes-assistant.git
    cd gov-schemes-assistant
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    SUPABASE_URL = "your_supabase_url"
    SUPABASE_SERVICE_ROLE_KEY = "your_key"
    MISTRAL_API_KEY = "your_mistral_key"
    TELEGRAM_BOT_TOKEN = "your_telegram_token"
    ```
4.  **Run Locally**:
    ```bash
    python frontend/app.py
    ```

## 🚢 Deployment
- **Web**: Deployed as a serverless application on **Vercel**.
- **Scraper**: Runs on a cron schedule via **GitHub Actions**.

## 📖 Technical Details
For a deep dive into the architecture and RAG pipeline, see [workflow.md](workflow.md).

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements.
