# VoiceStudy AI — System Architecture

## System Overview

VoiceStudy AI transforms spoken lecture content into structured
study material using Streamlit and Google's Gemini API.

```mermaid
flowchart TD

    A[Student] --> B[Streamlit Web Interface]

    B --> C[Microphone Recorder]

    C --> D[Audio Bytes]

    D --> E[Session State]

    E --> F[Gemini 3.6 Flash]

    F --> G[Lecture Transcription]

    G --> H[Study Material Form]

    H --> I[Dynamic Prompt]

    I --> F

    F --> J[Structured JSON]

    J --> K[AI Summary]

    J --> L[Flashcards]

    L --> M[Pandas DataFrame]

    M --> N[st.data_editor]

    N --> O[Review Progress]

    L --> P[CSV Download]

    G --> Q[AI Quiz Generator]

    Q --> R[MCQ Quiz]

    R --> S[Score & Explanations]