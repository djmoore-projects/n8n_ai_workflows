This repository is a curated portfolio of real-world AI automation systems built using n8n, LLMs, and cloud APIs to solve practical business problems across sales, proposals, onboarding, and contract execution.

These workflows are not demos or experiments. They are production-oriented systems designed with:
	•	Clear business outcomes
	•	Reliable data handling
	•	Human-in-the-loop safety
	•	Modular, extensible architecture

The goal of this repository is to showcase how AI can be operationalized to reduce manual work, accelerate revenue workflows, and improve execution quality across go-to-market teams.


What This Repository Demonstrates
	•	End-to-end AI orchestration using n8n
	•	LLM-driven reasoning with structured outputs (not free-form prompts)
	•	API-first automation across Google Workspace, PandaDoc, email, and CRM-style systems
	•	Event-driven and scheduled workflows
	•	Production design patterns for reliability, observability, and security

Included Workflows:


1. Sales Agent

Automated lead ingestion, CRM synchronization, and outbound follow-up orchestration

Key capabilities:
	•	Scheduled batch processing of lead lists
	•	CRM-style record creation and updates
	•	Automated follow-up logic with branching by engagement stage
	•	Rate-limited processing and state tracking

Primary value:
Creates a lightweight, automation-driven RevOps layer without requiring a full CRM rebuild.




2. Proposal Agent

AI-powered post-sales automation from call recording to proposal deck

Key capabilities:
	•	Webhook ingestion of recorded sales calls
	•	Transcript cleanup and normalization
	•	Structured information extraction using LLMs
	•	Automated proposal generation via templated Google Slides
	•	Internal review notification loop

Primary value:
Reduces proposal turnaround time and removes manual synthesis from the post-call process.




3. Onboarding & Contract Agent

Deal-close automation from CRM update to signed contract

Key capabilities:
	•	Event-driven triggers based on CRM state changes
	•	Multi-transcript reasoning across sales and closing calls
	•	Structured contract term extraction
	•	PandaDoc contract generation and delivery
	•	Milestone-based payment and timeline logic

Primary value:
Creates a seamless transition from “Closed Won” to signed agreement with minimal human effort.




Architecture & Design Philosophy

Across all workflows, the following principles are applied:
	•	Separation of concerns
Data ingestion, cleanup, reasoning, and output are isolated for reliability.
	•	Schema-first LLM usage
LLMs are constrained to structured outputs to reduce hallucinations and improve repeatability.
	•	Human-in-the-loop safety
Critical artifacts (proposals, contracts) always route through review steps.
	•	Composable systems
Tools like Google Sheets are used as interchangeable components, not hard dependencies.
	•	Production mindset
Designed for observability, credential safety, and extensibility.

Tech Stack
	•	Automation & Orchestration: n8n
	•	LLMs: Anthropic Claude (via OpenRouter), OpenAI-compatible interfaces
	•	Cloud & APIs: Google Workspace, PandaDoc, email services
	•	Data Layer: Google Sheets (CRM-lite, swappable)
	•	Future Work: Oracle Cloud Infrastructure (OCI) AI services

Security & Data Handling
	•	All workflows are exported with credentials removed
	•	API keys and secrets are managed via n8n credentials
	•	Sample inputs and outputs are fully anonymized
	•	No production data is included in this repository


About the Author

Built by Derek Moore, of AI Smartr, focused on designing and deploying AI-powered revenue workflows for sales teams, agencies, and professiona services companies.

This repository reflects hands-on work in:
	•	AI workflow architecture
	•	Revenue automation
	•	LLM reliability patterns
	•	API-driven system design

Contact: derek@aismartr.com
