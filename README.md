# FlashMind - AI Flashcard Generator

A modern, AI-powered web application that converts PDF documents into interactive flashcards using OpenAI and LangChain.

## Features
- **PDF Upload**: Drag and drop support for PDF files.
- **AI Generation**: Intelligent question and answer generation.
- **Interactive Viewer**: 3D flip animations and smooth navigation.
- **Dark Mode**: Beautiful dark/light theme toggle.
- **Responsive Design**: Works on all devices.

## Setup

1.  **Setup Virtual Environment & Install Dependencies**:
    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate it
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

3.  **Run the Application**:
    ```bash
    python app.py
    ```

4.  **Access**:
    Open your browser and navigate to `http://localhost:5000`.

## Tech Stack
- **Backend**: Flask, Python
- **AI**: LangChain, OpenAI GPT-3.5
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript
