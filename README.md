# Football Knowledge Graph RAG with MCP

## Overview

Football Knowledge Graph RAG is a Graph Retrieval-Augmented Generation (Graph RAG) system built using Neo4j, Large Language Models (LLMs), and the Model Context Protocol (MCP).

The system allows users to query a football knowledge graph using natural language. Questions are automatically translated into Cypher queries, executed against Neo4j, and transformed into human-readable answers using an LLM.

In addition, the system provides a Graph Builder that can automatically construct a knowledge graph from natural language text.

---

# System Architecture

## Graph RAG Pipeline

```text
User Question
      │
      ▼
Text-to-Cypher (LLM)
      │
      ▼
Cypher Query
      │
      ▼
Neo4j Knowledge Graph
      │
      ▼
Retrieved Data
      │
      ▼
Answer Generation (LLM)
      │
      ▼
Final Response
```

## Graph Builder Pipeline

```text
Natural Language Text
      │
      ▼
Entity & Relationship Extraction (LLM)
      │
      ▼
Structured Graph Data
      │
      ▼
Neo4j Knowledge Graph
```

---

# Technologies Used

* Python
* Neo4j Graph Database
* OpenRouter API
* Google Gemini 2.5 Flash
* MCP (Model Context Protocol)
* FastMCP

---

# Project Structure

```text
football-knowledge-graph-rag/

├── football_mcp.py
├── graph_rag.py
├── test.py
├── requirements.txt
├── .env.example
├── claude_desktop_config.example.json
└── README.md
```

---

# Code Documentation

## graph_rag.py

This module implements the Graph Retrieval-Augmented Generation (Graph RAG) workflow.

### Main Functions

### `test_connection()`

Verifies the connection to the Neo4j database.

### `generate_cypher(question)`

Converts a natural language question into a Cypher query using an LLM.

Example:

Input:

```text
Who are the players of Chelsea?
```

Generated Cypher:

```cypher
MATCH (a:Athlete)-[:PLAYS_FOR]->(c:Club)
WHERE c.name = "Chelsea F.C."
RETURN a.name AS athlete
LIMIT 20
```

---

### `execute_cypher(cypher)`

Executes a Cypher query against Neo4j and returns the results.

---

### `generate_answer(question, data)`

Converts retrieved graph data into a natural language response.

---

### `graph_rag(question)`

Main Graph RAG pipeline:

```text
Question
   ↓
Generate Cypher
   ↓
Execute Cypher
   ↓
Retrieve Graph Data
   ↓
Generate Answer
```

---

## football_mcp.py

This module implements the MCP server and exposes multiple tools for interacting with the knowledge graph.

### Available Tools

#### `ask_graph()`

Query the football knowledge graph using natural language.

#### `preview_graph()`

Preview entities and relationships before insertion into Neo4j.

#### `build_graph()`

Automatically construct a knowledge graph from natural language text.

#### `run_cypher()`

Execute custom Cypher queries directly on Neo4j.

#### `project_info()`

Display project information.

---

## test.py

Used for testing, experimentation, and development purposes.

---

# Knowledge Graph Schema

## Entities

### Athlete

Represents football players.

Examples:

```text
Cole Palmer
Bukayo Saka
Bruno Fernandes
```

### Club

Represents football clubs.

Examples:

```text
Chelsea F.C.
Arsenal F.C.
Manchester United F.C.
```

### Country

Represents player nationality or country of origin.

Examples:

```text
England
Germany
Brazil
```

---

## Relationships

### PLAYS_FOR

```text
(Athlete)-[:PLAYS_FOR]->(Club)
```

Example:

```text
Cole Palmer
    │
PLAYS_FOR
    ▼
Chelsea F.C.
```

---

### FROM

```text
(Athlete)-[:FROM]->(Country)
```

Example:

```text
Cole Palmer
    │
FROM
    ▼
England
```

---

# Cypher Query Logic

The system uses a Text-to-Cypher approach.

Example Question:

```text
Who are the players of Chelsea?
```

Generated Cypher:

```cypher
MATCH (a:Athlete)-[:PLAYS_FOR]->(c:Club)
WHERE c.name = "Chelsea F.C."
RETURN a.name AS athlete
LIMIT 20
```

---

Example Question:

```text
Which country contributes the most players to Arsenal?
```

Generated Cypher:

```cypher
MATCH (a:Athlete)-[:PLAYS_FOR]->(c:Club),
      (a)-[:FROM]->(country:Country)
WHERE c.name = "Arsenal F.C."
RETURN country.name AS country,
       count(*) AS total
ORDER BY total DESC
LIMIT 10
```

---

# AI Pipeline Explanation

The AI workflow consists of three main stages.

## Stage 1 — Natural Language to Cypher

User question:

```text
Who plays for Chelsea?
```

The LLM translates the question into a valid Cypher query based on the graph schema.

---

## Stage 2 — Graph Retrieval

The generated Cypher query is executed against Neo4j.

Example result:

```json
[
  {
    "athlete": "Cole Palmer"
  },
  {
    "athlete": "Enzo Fernandez"
  }
]
```

---

## Stage 3 — Natural Language Answer Generation

The retrieved graph data is passed back to the LLM to generate a human-readable response.

Example:

```text
The players currently associated with Chelsea in the knowledge graph are Cole Palmer and Enzo Fernandez.
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Fachreza28/football-knowledge-graph-rag.git

cd football-knowledge-graph-rag
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file:

```env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

OPENROUTER_API_KEY=your_api_key

MODEL_NAME=google/gemini-2.5-flash
```

---

# Running the Project

Start the MCP server:

```bash
python football_mcp.py
```

Expected output:

```text
STARTING MCP SERVER...
```

---

# Example Queries

```text
Who plays for Chelsea?

Who plays for Arsenal?

Which country contributes the most players to Arsenal?

Which players are from England?

Which club does Cole Palmer play for?
```

---


---

# Author

**Fachreza Aptadhi Kurniawan**

# Co-Author

**Sultan Alamsyah Mubarok**

Football Knowledge Graph RAG Project using Neo4j, MCP, Graph RAG, and Large Language Models.
