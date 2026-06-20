from mcp.server.fastmcp import FastMCP
from graph_rag import graph_rag, call_openrouter

from neo4j import GraphDatabase
import atexit
import json

import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# NEO4J CONNECTION
# =====================================================

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
    )
)

atexit.register(driver.close)

# =====================================================
# MCP SERVER
# =====================================================

mcp = FastMCP("FootballKnowledgeGraph")

# =====================================================
# GRAPH BUILDER HELPER
# =====================================================

def extract_graph_from_text(text: str):

    prompt = f"""
You are a football knowledge graph extractor.

Entity Types:
- Athlete
- Club
- Country

Relationship Types:
- PLAYS_FOR
- FROM

Return ONLY valid JSON.

Example:

{{
  "entities": [
    {{
      "label": "Athlete",
      "name": "Cole Palmer"
    }},
    {{
      "label": "Club",
      "name": "Chelsea F.C."
    }},
    {{
      "label": "Country",
      "name": "England"
    }}
  ],
  "relationships": [
    {{
      "source": "Cole Palmer",
      "type": "PLAYS_FOR",
      "target": "Chelsea F.C."
    }},
    {{
      "source": "Cole Palmer",
      "type": "FROM",
      "target": "England"
    }}
  ]
}}

Text:
{text}
"""

    content = call_openrouter(
        prompt,
        max_tokens=800
    )

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(content)

# =====================================================
# RAG TOOL
# =====================================================

@mcp.tool()
def ask_graph(question: str) -> str:
    """
    Tanya Knowledge Graph sepak bola
    berdasarkan data Wikidata + DBpedia.
    """
    return graph_rag(question)

# =====================================================
# GRAPH BUILDER PREVIEW
# =====================================================

@mcp.tool()
def preview_graph(text: str) -> str:
    """
    Preview entity dan relationship
    yang akan dibuat tanpa insert Neo4j.
    """

    try:

        data = extract_graph_from_text(text)

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

    except Exception as e:
        return f"Error: {str(e)}"

# =====================================================
# GRAPH BUILDER INSERT
# =====================================================

@mcp.tool()
def build_graph(text: str) -> str:
    """
    Bangun graph dari teks natural language.
    """

    try:

        data = extract_graph_from_text(text)

        allowed_labels = {
            "Athlete",
            "Club",
            "Country"
        }

        allowed_relationships = {
            "PLAYS_FOR",
            "FROM"
        }

        with driver.session() as session:

            # ENTITY

            for entity in data["entities"]:

                label = entity["label"]

                if label not in allowed_labels:
                    continue

                session.run(
                    f"""
                    MERGE (n:{label} {{
                        name: $name
                    }})
                    """,
                    name=entity["name"]
                )

            # RELATIONSHIP

            for rel in data["relationships"]:

                rel_type = rel["type"]

                if rel_type not in allowed_relationships:
                    continue

                query = f"""
                MATCH (a {{
                    name: $source
                }})

                MATCH (b {{
                    name: $target
                }})

                MERGE (a)-[:{rel_type}]->(b)
                """

                session.run(
                    query,
                    source=rel["source"],
                    target=rel["target"]
                )

        return json.dumps(
            {
                "status": "success",
                "entities_added": len(data["entities"]),
                "relationships_added": len(data["relationships"])
            },
            indent=2
        )

    except Exception as e:
        return f"Error: {str(e)}"

# =====================================================
# PROJECT INFO
# =====================================================

@mcp.tool()
def project_info() -> str:
    """
    Informasi project
    """

    return """
Football Knowledge Graph

Data Source:
- Wikidata
- DBpedia

Entity:
- Athlete
- Club
- Country

Graph Analytics:
- Degree Centrality
- Jaccard Similarity
- Louvain Community Detection

Graph Machine Learning:
- FastRP Embedding
- KNN Similarity
- K-Means Clustering

LLM Features:
- Text-to-Cypher
- Graph Builder

Integration:
- MCP
"""

# =====================================================
# RUN CYPHER
# =====================================================

@mcp.tool()
def run_cypher(query: str) -> str:
    """
    Jalankan query Cypher apapun ke Neo4j.
    """

    try:

        with driver.session() as session:

            result = session.run(query)

            rows = result.data()

            if rows:
                return "\n".join(
                    str(row)
                    for row in rows
                )

            summary = result.consume()

            return (
                f"Query executed successfully.\n"
                f"Nodes created: {summary.counters.nodes_created}\n"
                f"Nodes deleted: {summary.counters.nodes_deleted}\n"
                f"Relationships created: {summary.counters.relationships_created}\n"
                f"Properties set: {summary.counters.properties_set}"
            )

    except Exception as e:
        return f"Error: {str(e)}"

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("STARTING MCP SERVER...")

    mcp.run(
        transport="streamable-http"
    )

    print("SERVER STOPPED")