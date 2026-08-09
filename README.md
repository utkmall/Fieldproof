# FieldProof

An AI-assisted crop insurance claim assessment system that combines multi-agent processing, weather intelligence, and machine learning to support first-level claim verification.

## Highlights

- Multi-agent claim assessment pipeline
- Feature extraction and claim preprocessing
- Weather-based claim analysis
- ML-based crop loss prediction
- Classification and regression models for claim assessment
- Validation layer for assessment outputs
- Decision agent for final claim assessment
- Web-based claim assessment dashboard
- Modular pipeline for extending individual assessment stages

## Tech Stack

- Python
- Flask
- Pandas, NumPy
- Scikit-learn
- Next.js, React, TypeScript
- Classification and regression models

## How It Works

A claim is processed through multiple specialized agents before producing a final assessment.

```text
Claim
  |
  v
Feature Agent
  |
  +------------------+
  |                  |
  v                  v
Weather Agent     ML Agent
  |                  |
  +--------+---------+
           |
           v
   Validation Agent
           |
           v
    Decision Agent
           |
           v
   Claim Assessment
Multi-Agent Layer
Feature Agent — extracts and prepares relevant claim features
Weather Agent — analyzes weather conditions associated with the claim
ML Agent — generates crop loss predictions using trained models
Validation Agent — validates the generated assessment
Decision Agent — combines the available outputs into a final assessment
Getting Started
1. Clone and setup
git clone <repository-url>
cd fieldproof

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
2. Run the backend
python api/main.py
3. Run the frontend
cd frontend
npm install
npm run dev
Testing

Run the pipeline test with:

python test_pipeline.py
Project Structure
agents/       Multi-agent assessment layer
api/          Backend API
core/         Crop loss prediction engine
pipeline/     Claim verification workflow
v1.0.0/       Trained models and metadata
frontend/     Web dashboard
Models

The v1.0.0 directory contains the trained model artifacts used by the assessment pipeline.

classifier.pkl — claim classification model
regressor.pkl — crop loss regression model
crop_averages.json — crop-level reference data
metadata.json — model and dataset metadata
Development

FieldProof is structured as a modular assessment pipeline so that individual agents, models, and processing stages can be improved independently.

The current architecture focuses on automated first-level assessment while keeping human review as part of the overall claim verification process.

Future Scope
Satellite and remote-sensing data integration
Crop-specific prediction models
Automated anomaly and fraud detection
Improved claim prioritization
Expanded weather intelligence
Integration with large-scale crop insurance workflows
