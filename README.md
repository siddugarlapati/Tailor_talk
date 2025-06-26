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

## Usage
- Open the Streamlit app and chat to book appointments. 