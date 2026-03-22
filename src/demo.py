"""Pre-cached demo results for hackathon presentations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Pre-cached demo research result for "Impact of AI on healthcare"
DEMO_QUERIES: dict[str, dict[str, Any]] = {
    "Impact of AI on healthcare": {
        "query": "Impact of AI on healthcare",
        "summary": (
            "Artificial intelligence is rapidly transforming healthcare, with applications ranging from "
            "diagnostic imaging to drug discovery. Machine learning models now match or exceed human "
            "radiologists in detecting certain cancers from medical scans. AI-powered tools are "
            "accelerating drug development timelines by predicting molecular interactions, reducing "
            "the average 10-year discovery cycle. Natural language processing enables automated "
            "analysis of electronic health records, improving clinical decision support. However, "
            "challenges remain around data privacy, algorithmic bias, and regulatory approval "
            "frameworks for AI-based medical devices."
        ),
        "key_sentences": [
            "Deep learning models achieved 94.5% accuracy in detecting breast cancer from mammograms, matching expert radiologists.",
            "AI-driven drug discovery has reduced early-stage development costs by an estimated 30-40%.",
            "The global AI in healthcare market is projected to reach $187.95 billion by 2030.",
            "Natural language processing can extract structured data from unstructured clinical notes with over 90% accuracy.",
            "Algorithmic bias in training data remains a critical concern, with studies showing disparities across demographic groups.",
        ],
        "entities": {
            "ORG": ["WHO", "FDA", "Google Health", "DeepMind", "IBM Watson Health"],
            "GPE": ["United States", "United Kingdom", "China", "European Union"],
            "TECHNOLOGY": ["Deep Learning", "Natural Language Processing", "Computer Vision", "Reinforcement Learning"],
            "DISEASE": ["Cancer", "Diabetes", "Alzheimer's", "COVID-19"],
        },
        "key_phrases": [
            "artificial intelligence in healthcare",
            "machine learning diagnostics",
            "drug discovery pipeline",
            "electronic health records",
            "clinical decision support",
            "medical imaging analysis",
            "predictive analytics",
            "algorithmic bias",
            "regulatory frameworks",
            "precision medicine",
        ],
        "statistics": [
            "The global AI in healthcare market is projected to reach $187.95 billion by 2030.",
            "Deep learning models achieved 94.5% accuracy in breast cancer detection from mammograms.",
            "AI-driven drug discovery reduces early-stage costs by an estimated 30-40%.",
            "Over 80% of healthcare organizations plan to adopt AI tools by 2025.",
            "NLP systems process clinical notes with over 90% accuracy for structured data extraction.",
        ],
        "claims": [
            "According to a 2024 study published in Nature Medicine, AI diagnostic tools matched or exceeded specialist performance in 14 out of 20 clinical tasks evaluated.",
            "Research from Stanford found that AI models trained on diverse datasets showed 15% fewer diagnostic errors across demographic groups.",
            "The FDA has approved over 500 AI-enabled medical devices as of 2024, up from fewer than 100 in 2019.",
            "A meta-analysis demonstrated that AI-assisted radiology reduced diagnostic turnaround time by 47%.",
        ],
        "consensus_points": [
            "Multiple sources agree: AI shows strong potential in medical imaging and diagnostics.",
            "Sources consistently report accelerated drug discovery timelines with AI assistance.",
            "Broad consensus on the need for regulatory frameworks specific to AI medical devices.",
        ],
        "conflict_points": [
            "Unique to WHO report: concerns about AI widening healthcare access gaps in developing nations.",
            "Unique to industry analysis: optimistic 5-year adoption timeline vs. academic sources suggesting 10+ years for full integration.",
        ],
        "sources": [
            {
                "url": "https://www.nature.com/articles/s41591-024-example",
                "title": "AI in Clinical Medicine: A Comprehensive Review",
                "credibility_score": 0.95,
                "credibility_rating": "High",
                "word_count": 8420,
                "snippet": "Comprehensive review of AI applications across clinical specialties...",
            },
            {
                "url": "https://www.who.int/publications/ai-healthcare-2024",
                "title": "WHO Report: Artificial Intelligence for Health",
                "credibility_score": 0.92,
                "credibility_rating": "High",
                "word_count": 12300,
                "snippet": "Global perspectives on AI adoption in healthcare systems...",
            },
            {
                "url": "https://www.sciencedirect.com/science/article/ai-drug-discovery",
                "title": "Machine Learning in Drug Discovery: Current Progress",
                "credibility_score": 0.90,
                "credibility_rating": "High",
                "word_count": 6750,
                "snippet": "Review of ML approaches in pharmaceutical research and development...",
            },
            {
                "url": "https://arxiv.org/abs/2024.medical-nlp",
                "title": "NLP for Electronic Health Records: Advances and Challenges",
                "credibility_score": 0.85,
                "credibility_rating": "High",
                "word_count": 5200,
                "snippet": "Survey of NLP techniques applied to clinical text processing...",
            },
            {
                "url": "https://www.fda.gov/medical-devices/ai-ml-enabled-devices",
                "title": "FDA: AI/ML-Enabled Medical Devices",
                "credibility_score": 0.93,
                "credibility_rating": "High",
                "word_count": 3400,
                "snippet": "Official FDA listing and regulatory framework for AI medical devices...",
            },
        ],
    },
    "Quantum computing breakthroughs 2024": {
        "query": "Quantum computing breakthroughs 2024",
        "summary": (
            "Quantum computing achieved several milestones in 2024, with Google's Willow chip "
            "demonstrating error correction below the fault-tolerance threshold for the first time. "
            "IBM launched its 1,121-qubit Condor processor, while Microsoft and Quantinuum achieved "
            "reliable logical qubits. These advances bring practical quantum advantage closer for "
            "problems in cryptography, materials science, and optimization. However, current systems "
            "still require extreme cooling and remain limited to specialized tasks."
        ),
        "key_sentences": [
            "Google's Willow quantum chip performed a computation in under 5 minutes that would take classical supercomputers 10 septillion years.",
            "IBM's Condor processor reached 1,121 superconducting qubits, the largest gate-based quantum processor built.",
            "Microsoft and Quantinuum demonstrated the first reliable logical qubits with error rates below threshold.",
            "Quantum computing is expected to break current RSA encryption within 10-15 years according to NIST.",
            "The global quantum computing market is projected to reach $65 billion by 2030.",
        ],
        "entities": {
            "ORG": ["Google", "IBM", "Microsoft", "Quantinuum", "NIST", "IonQ"],
            "PRODUCT": ["Willow", "Condor", "Eagle", "Osprey"],
            "GPE": ["United States", "China", "Canada", "Japan"],
        },
        "key_phrases": [
            "quantum error correction",
            "fault-tolerant quantum computing",
            "superconducting qubits",
            "quantum advantage",
            "post-quantum cryptography",
            "logical qubits",
            "quantum supremacy",
            "topological qubits",
        ],
        "statistics": [
            "Google's Willow chip completed a benchmark computation in under 5 minutes vs. 10 septillion years classically.",
            "IBM's Condor processor contains 1,121 superconducting qubits.",
            "The global quantum computing market is projected to reach $65 billion by 2030.",
            "NIST estimates RSA-2048 could be broken by a sufficiently large quantum computer within 10-15 years.",
        ],
        "claims": [
            "Google researchers demonstrated that increasing qubit count actually reduced error rates, a key milestone for scalable quantum computing.",
            "According to IBM's roadmap, quantum systems with 100,000 qubits are planned for 2033.",
            "Research published in Nature showed that logical qubit error rates dropped below physical qubit error rates for the first time.",
        ],
        "consensus_points": [
            "Multiple sources agree: 2024 marked a turning point for quantum error correction.",
            "Broad consensus that practical quantum advantage for real-world problems is still 5-10 years away.",
        ],
        "conflict_points": [
            "Unique to Google: claims of quantum supremacy challenged by classical algorithm improvements.",
            "Unique to academic sources: skepticism about industry timeline projections for fault-tolerant systems.",
        ],
        "sources": [
            {
                "url": "https://www.nature.com/articles/quantum-willow-2024",
                "title": "Google Willow: Below-Threshold Quantum Error Correction",
                "credibility_score": 0.95,
                "credibility_rating": "High",
                "word_count": 7200,
                "snippet": "Demonstration of exponential error suppression in a superconducting quantum processor...",
            },
            {
                "url": "https://research.ibm.com/blog/condor-quantum-processor",
                "title": "IBM Condor: 1,121-Qubit Quantum Processor",
                "credibility_score": 0.85,
                "credibility_rating": "High",
                "word_count": 4500,
                "snippet": "IBM's largest quantum processor and the path to quantum-centric supercomputing...",
            },
            {
                "url": "https://arxiv.org/abs/2024.logical-qubits",
                "title": "Reliable Logical Qubits with Trapped Ions",
                "credibility_score": 0.87,
                "credibility_rating": "High",
                "word_count": 5800,
                "snippet": "Microsoft and Quantinuum demonstrate fault-tolerant logical qubit operations...",
            },
            {
                "url": "https://www.nist.gov/quantum-computing-standards",
                "title": "NIST Post-Quantum Cryptography Standards",
                "credibility_score": 0.93,
                "credibility_rating": "High",
                "word_count": 3200,
                "snippet": "NIST finalizes post-quantum cryptography standards for government use...",
            },
        ],
    },
}


def get_demo_queries() -> list[str]:
    """Return available demo query strings."""
    return list(DEMO_QUERIES.keys())


def get_demo_result(query: str) -> dict[str, Any] | None:
    """Return pre-cached demo result for a query, or None."""
    return DEMO_QUERIES.get(query)
