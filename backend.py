from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD"))
)

@app.get("/health")
def health():
    with driver.session() as s:
        s.run("RETURN 1")
    return {"status": "ok"}

@app.get("/symptoms")
def symptoms():
    with driver.session() as s:
        result = s.run("MATCH (s:Symptom) RETURN s.name AS name, s.uid AS id ORDER BY s.name")
        return [{"id": r["id"], "name": r["name"]} for r in result]

@app.get("/ask")
def ask(q: str):
    with driver.session() as s:
        result = s.run("""
            MATCH (s:Symptom {name: $q})-[r:CAUSED_BY]->(c:Cause)
            OPTIONAL MATCH (c)-[:FIXED_BY]->(step:Step)
            RETURN r.priority AS priority, c.name AS cause, c.check_time AS time, step.name AS step
            ORDER BY r.priority
        """, q=q)
        return [dict(r) for r in result]
