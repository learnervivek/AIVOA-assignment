import logging
import datetime
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.ai.state import RCAWorkflowState
from app.ai.nodes.extract import extract_deviation_fields
from app.ai.nodes.audit import detect_missing_evidence
from app.ai.nodes.rca import perform_rca_analysis
from app.ai.nodes.capa import recommend_capa
from app.ai.nodes.refine import refine_rca_and_capa

logger = logging.getLogger("pharma_rca.ai.graph")


def build_rca_graph():
    """
    Constructs the core 4-node LangGraph RCA workflow:
    START -> extract_deviation_fields -> detect_missing_evidence -> perform_rca_analysis -> recommend_capa -> END
    """
    workflow = StateGraph(RCAWorkflowState)

    # Add nodes
    workflow.add_node("extract_deviation_fields", extract_deviation_fields)
    workflow.add_node("detect_missing_evidence", detect_missing_evidence)
    workflow.add_node("perform_rca_analysis", perform_rca_analysis)
    workflow.add_node("recommend_capa", recommend_capa)

    # Define execution edges
    workflow.add_edge(START, "extract_deviation_fields")
    workflow.add_edge("extract_deviation_fields", "detect_missing_evidence")
    workflow.add_edge("detect_missing_evidence", "perform_rca_analysis")
    workflow.add_edge("perform_rca_analysis", "recommend_capa")
    workflow.add_edge("recommend_capa", END)

    return workflow.compile()


def build_refinement_graph():
    """
    Constructs the LangGraph refinement workflow for user follow-up instructions:
    START -> refine_rca_and_capa -> END
    """
    workflow = StateGraph(RCAWorkflowState)
    workflow.add_node("refine_rca_and_capa", refine_rca_and_capa)
    workflow.add_edge(START, "refine_rca_and_capa")
    workflow.add_edge("refine_rca_and_capa", END)
    return workflow.compile()


# Compiled singleton graph runners
rca_graph_app = build_rca_graph()
refinement_graph_app = build_refinement_graph()


async def run_rca_workflow(
    raw_text: str,
    source_type: str = "text",
    preferred_methodology: str = "fishbone",
) -> Dict[str, Any]:
    """
    Executes the full LangGraph RCA pipeline asynchronously.
    """
    initial_state: RCAWorkflowState = {
        "raw_text": raw_text,
        "source_type": source_type,
        "preferred_methodology": preferred_methodology,
        "deviation_fields": {},
        "missing_evidence": [],
        "five_whys_data": [],
        "fishbone_6m_data": {
            "man": [],
            "machine": [],
            "material": [],
            "method": [],
            "measurement": [],
            "environment": [],
        },
        "potential_root_causes": [],
        "capa_recommendations": [],
        "execution_logs": [
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] LangGraph RCA workflow initialized for source: {source_type}"
        ],
    }

    try:
        final_state = await rca_graph_app.ainvoke(initial_state)
        return final_state
    except Exception as exc:
        logger.error(f"Error executing LangGraph RCA workflow: {exc}", exc_info=True)
        # Fallback to synchronous invocation if ainvoke encounters event loop issues
        return rca_graph_app.invoke(initial_state)


async def run_refinement_workflow(
    current_state: Dict[str, Any],
    instruction: str,
) -> Dict[str, Any]:
    """
    Executes the LangGraph refinement workflow with a user instruction.
    """
    input_state: RCAWorkflowState = {
        **current_state,
        "refinement_instruction": instruction,
        "execution_logs": current_state.get("execution_logs", []).copy(),
    }
    input_state["execution_logs"].append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] LangGraph refinement started: '{instruction}'"
    )

    try:
        final_state = await refinement_graph_app.ainvoke(input_state)
        return final_state
    except Exception as exc:
        logger.error(f"Error executing LangGraph refinement workflow: {exc}", exc_info=True)
        return refinement_graph_app.invoke(input_state)
