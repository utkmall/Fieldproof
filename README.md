# FieldProof

AI-assisted crop insurance claim assessment system that uses weather intelligence, machine learning, and a multi-agent architecture to support first-level claim verification.

## Overview

FieldProof analyzes crop insurance claims using claim features, weather conditions, and trained ML models to generate a preliminary assessment. The system is designed to reduce manual verification effort and help prioritize claims for further review.

## Multi-Agent Layer

FieldProof uses specialized agents for different stages of claim assessment:

- **Feature Agent** — extracts and prepares claim features
- **Weather Agent** — analyzes relevant weather conditions
- **ML Agent** — generates crop loss predictions
- **Validation Agent** — validates the assessment
- **Decision Agent** — produces the final claim assessment

## Tech Stack

**Backend:** Python, Flask, Pandas, NumPy, Scikit-learn

**Frontend:** Next.js, React, TypeScript

**ML:** Classification, Regression

## Project Structure

```text
agents/       Multi-agent assessment layer
api/          Backend API
core/         Prediction engine
pipeline/     Claim verification workflow
v1.0.0/       Trained models and metadata
frontend/     Web dashboard
Getting Started
git clone <repository-url>
cd fieldproof

pip install -r requirements.txt

python api/main.py

For the frontend:

cd frontend
npm install
npm run dev
Testing
python test_pipeline.py
Future Scope
Satellite and remote-sensing integration
Crop-specific prediction models
Anomaly and fraud detection
Automated claim prioritization
