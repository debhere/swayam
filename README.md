# Swayam: Your AI-Powered Policy Assistant

Swayam provides the policy holders' the information as per the official Life Insurance of India (LIC) Policy documents. Users can verify or compare the AI response with the source documents given in the citation. Swayam is multi-modal in nature i.e., users can communicate in both text or voice with Swayam. India is a vast country and still has a large user base ho are yet to be connected with the country's digital revolution. Hence, along with English, Swayam offers voice command support in multiple Indian languages including - Bengali, Hindi, Marathi, and Kannada.

## Problem Statement

### Context

The Life Insurance Corporation of India (LIC) is the backbone of India’s retail financial savings, managing a monumental ₹59,03,876 Crore in Total Assets and serving as the country's dominant life insurer. Across its vast portfolio—which spans traditional Life Insurance, Pension/Annuity plans, Unit-Linked Pension products, and socially critical Micro-Insurance schemes—the corporation has a massive 25.35 Crore individual policies in force.

### The Problem

Despite the staggering financial scale and an annual subscription volume where 1.84 Crore new policies are sold every year, a profound information asymmetry and accessibility gap exists for the end consumer.

- Policy terms, vesting rules for pensions, market-linked performance thresholds for unit-linked products, and micro-insurance claim conditions are locked inside complex, highly technical policy legal documents.

- This fragmented data is notoriously difficult for a layperson to self-retrieve or interpret via standard legacy portals, millions of policyholders are left entirely at the mercy of individual insurance agents for even minor informational queries (e.g., surrender value timelines, bonus accumulation metrics, or pension payouts)

- This over-reliance on a network of 14.72 Lakh agents creates an administrative bottleneck, delays customer decision-making, and leaves non-digitized policyholders vulnerable to misinterpretation or misinformation.

## Solution

To bridge this consumer-accessibility gap, this project introduces an intelligent, enterprise-grade Retrieval-Augmented Generation (RAG) based Chatbot. By ingesting and mapping the official product prospectuses, premium tables, and sample policy conditions directly from LIC's active product catalog, the RAG chatbot eliminates traditional information barriers.

Instead of forcing users to navigate dense, multi-page PDFs filled with insurance jargon, the chatbot allows policyholders to query specific plan parameters (such as grace periods, lock-ins, or maturity criteria) in plain language. It instantly extracts context-grounded, completely accurate answers, systematically eliminating agent dependency and democratizing retail insurance data for millions.

## Product Scope

Swayam is equipped to provide answers on the policies pertaining to Insurance plans, Pension plans, Unit linked plans, and Micro insurance plans.

Plans that are withdrawn by LIC, are beyond the scope of Swayam's ***knowledge-base***.


## Technology Stack

### Frontend

```bash
ReactJS (Web-App)
Telegram
```

### Backend

```bash
Python >= 3.11
FastAPI
LlamaIndex >= 2.8
LangChain
LangGraph
```

## Risks

## Assumptions & Limitations


## Issues


## Dependencies


### Ingestion

```bash
uv run python -m ingestion.downloader
```
downloader.py is the controller
insurance.py is manages the insurance related documents
other_products.py is for all other products

Approach is simple:
1) Navigate to product url
    Insurance specific
        1.1) Capture the category urls
        1.2) Loop through the category urls
2) Capture the policy urls
3) Loop through the policy urls
4) Get all the document links for the selected policy url
5) Download the documents in pdf format
6) Parse the pdf files into mardown files

[windows powershell] need to check
```bash
tree /F /A >folder-structure.txt 
```

```bash
tree > folder-structure.txt
```
if nor installed

```bash
sudo apt install tree
```

### Extraction

#### Approach

Try 2-3 different extract library


