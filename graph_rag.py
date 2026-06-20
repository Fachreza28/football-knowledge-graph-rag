from neo4j import GraphDatabase
import requests

import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# CONFIG
# =====================================================

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "google/gemini-2.5-flash"
)

# =====================================================
# CONNECT NEO4J
# =====================================================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# =====================================================
# TEST CONNECTION
# =====================================================

def test_connection():

    query = """
    MATCH (n)
    RETURN count(n) AS total
    """

    with driver.session() as session:

        result = session.run(query)

        row = result.single()

        print("\n=== CONNECTION SUCCESS ===")
        print("Total Nodes:", row["total"])
        print("==========================\n")


# =====================================================
# SHOW CLUBS
# =====================================================

def get_clubs():

    query = """
    MATCH (c:Club)
    RETURN c.name AS club
    """

    with driver.session() as session:

        results = session.run(query)

        clubs = []

        for row in results:

            clubs.append(
                row["club"]
            )

        return clubs


# =====================================================
# OPENROUTER CALL
# =====================================================

def call_openrouter(prompt, max_tokens=500):

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":
                "application/json"
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens
        }
    )

    data = response.json()

    if "error" in data:

        raise Exception(str(data))

    return data["choices"][0]["message"]["content"]


# =====================================================
# STEP 1
# NATURAL LANGUAGE -> CYPHER
# =====================================================

def generate_cypher(question):

    schema = """
Graph Schema

(Athlete)-[:PLAYS_FOR]->(Club)
(Athlete)-[:FROM]->(Country)

Known Club Names:
- Chelsea F.C.
- Arsenal F.C.
- Manchester United F.C.

Node Properties:
Athlete.name
Club.name
Country.name

IMPORTANT:
Jika user menyebut:
- Chelsea -> gunakan Chelsea F.C.
- Arsenal -> gunakan Arsenal F.C.
- Manchester United -> gunakan Manchester United F.C.

Return ONLY Cypher.

Examples:

Question:
Siapa saja pemain Chelsea?

Cypher:
MATCH (a:Athlete)-[:PLAYS_FOR]->(c:Club)
WHERE c.name = "Chelsea F.C."
RETURN a.name AS athlete
LIMIT 20

Question:
Negara mana yang paling banyak menyumbang pemain ke Arsenal?

Cypher:
MATCH (a:Athlete)-[:PLAYS_FOR]->(c:Club),
      (a)-[:FROM]->(country:Country)
WHERE c.name = "Arsenal F.C."
RETURN country.name AS country,
       count(*) AS total
ORDER BY total DESC
LIMIT 10
"""

    prompt = f"""
{schema}

Question:
{question}

Generate Cypher Query:
"""

    cypher = call_openrouter(
        prompt,
        max_tokens=300
    )

    cypher = cypher.replace("```cypher", "")
    cypher = cypher.replace("```", "")
    cypher = cypher.strip()

    return cypher


# =====================================================
# STEP 2
# EXECUTE CYPHER
# =====================================================

def execute_cypher(cypher):

    with driver.session() as session:

        result = session.run(cypher)

        rows = []

        for row in result:

            rows.append(
                dict(row)
            )

        return rows


# =====================================================
# STEP 3
# DATA -> NATURAL LANGUAGE
# =====================================================

def generate_answer(question, data):

    prompt = f"""
Kamu adalah analis Football Knowledge Graph.

Pertanyaan:
{question}

Data hasil query Neo4j:
{data}

Instruksi:
- Jawab dalam Bahasa Indonesia
- Gunakan hanya data yang tersedia
- Jika data kosong, katakan data tidak ditemukan
"""

    return call_openrouter(
        prompt,
        max_tokens=500
    )


# =====================================================
# GRAPH RAG
# =====================================================

def graph_rag(question):

    try:

        # 1. Generate Cypher
        cypher = generate_cypher(
            question
        )

        print("\n==============================")
        print("GENERATED CYPHER")
        print("==============================")
        print(cypher)

        # 2. Retrieve from Neo4j
        data = execute_cypher(
            cypher
        )

        print("\n==============================")
        print("RETRIEVED DATA")
        print("==============================")
        print(data)

        # 3. Generate Answer
        answer = generate_answer(
            question,
            data
        )

        return answer

    except Exception as e:

        return f"ERROR: {str(e)}"
