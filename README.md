# Tialor Talk - Conversational Appointment Booking Agent

## Overview
Conversational AI agent to help users book appointments on Google Calendar via chat.

## Tech Stack
- Backend: FastAPI, LangGraph, Google Calendar API
- Frontend: Streamlit

## Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Set up Google Calendar API credentials (see Google documentation).
4. `uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## OpenAI API Key Required

To use this app, you must have your own OpenAI API key:

1. Go to https://platform.openai.com/account/api-keys and sign in or create an account.
2. Click "Create new secret key" and copy the generated key (it starts with sk-...).
3. Set this key as an environment variable named `OPENAI_API_KEY` in your deployment platform or your local environment.
   - On your local machine, you can set it in your terminal before running the backend:
     ```sh
     export OPENAI_API_KEY=sk-...  # Linux/Mac
     set OPENAI_API_KEY=sk-...     # Windows
     ```
   - On Render or other cloud platforms, add it in the environment variables/settings section.

**Never share your API key publicly or commit it to your code repository.**

## Usage
- Open the Streamlit app and chat to book appointments. 