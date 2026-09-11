import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.graph.workflow import compile_graph
from src.logging.logger import logging

app = FastAPI(
    title="Corporate Credit Due Diligence API",
    description="LangGraph-powered agent for credit risk extraction and scoring.",
    version="1.0.0"
)

graph = compile_graph()

class DueDiligenceRequest(BaseModel):
    raw_document: str
    thread_id: str = "default_thread_1"

class ApprovalRequest(BaseModel):
    thread_id: str
    approve: bool

async def graph_event_generator(request: DueDiligenceRequest):
    """
    Executes the LangGraph state machine and yields Server-Sent Events (SSE)
    as each node completes its execution[cite: 4].
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    initial_state = {"raw_document": request.raw_document}

    logging.info(f"Starting graph execution for thread: {request.thread_id}")

    try:
        async for event in graph.astream(initial_state, config, stream_mode="updates"):
            event_json = json.dumps(event, default=str)
            yield f"data: {event_json}\n\n"

        current_state = graph.get_state(config)
        if current_state.next:
            pause_data = json.dumps({
                "status": "interrupted", 
                "pending_node": current_state.next[0]
            })
            yield f"data: {pause_data}\n\n"
            
    except Exception as e:
        logging.error(f"Graph execution failed: {e}")
        error_json = json.dumps({"error": str(e)})
        yield f"data: {error_json}\n\n"

@app.post("/analyze", response_class=StreamingResponse)
async def analyze_document(request: DueDiligenceRequest):
    """
    Endpoint to ingest a raw SEC document and stream back the agent's progress
    (Extraction -> Scoring -> Synthesis/Routing)[cite: 4].
    """
    if not request.raw_document.strip():
        raise HTTPException(status_code=400, detail="raw_document cannot be empty.")
        
    return StreamingResponse(
        graph_event_generator(request), 
        media_type="text/event-stream"
    )

@app.post("/approve")
async def approve_review(request: ApprovalRequest):
    """
    Endpoint to resume graph execution after a human reviews the high-risk metrics.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    current_state = graph.get_state(config)

    if not current_state.next:
        raise HTTPException(status_code=400, detail="No pending human review found for this thread.")

    if not request.approve:
        return {"status": "aborted", "message": "Execution aborted by human."}

    events = []
    async for event in graph.astream(None, config, stream_mode="updates"):
        events.append(list(event.keys())[0])

    final_state = graph.get_state(config)
    memo = final_state.values.get("underwriting_memo", "No memo generated.")

    return {
        "status": "resumed_and_completed",
        "nodes_executed": events,
        "final_memo": memo
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)