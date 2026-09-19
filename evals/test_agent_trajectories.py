import pytest
from src.graph.workflow import compile_graph
from src.entity.schema import CreditFeaturesSchema

@pytest.fixture(scope="module")
def agent_graph():
    return compile_graph()

GOLDEN_CASES = [
    (
        "Applicant seeks a $1,000,000 loan, 60 month term at 15%. Monthly installment $23,789. Revenue $15,000, DTI 85%, 4 bankruptcies.", 
        True, 1000000.0, 85.0
    ),
    (
        "Requesting $12,000 for home improvement, 36 months at 5.5%. Installment $362. Income $150,000, DTI 12%, 0 bankruptcies.", 
        False, 12000.0, 12.0
    ),
    (
        "$50,000 commercial loan, 24 months, 25% interest. $2,200 monthly. Income $15,000. DTI 85%. 4 previous bankruptcies.", 
        True, 50000.0, 85.0
    ),
    (
        "Loan amount $5,000. Term 12 months. Interest 4%. Income $60,000. DTI 15%. No public records.", 
        True, 5000.0, 15.0
    ),
    (
        "Seeking $750,000. Revenue $40,000. DTI 90%. 3 bankruptcies. 60 month term, 18% rate.", 
        True, 750000.0, 90.0
    ),
    (
        "Personal loan of $25,000. Income $120,000. DTI 20%. Term 48 months, interest 6%. Rents home.", 
        False, 25000.0, 20.0
    ),
    (
        "High risk flag: $2,000,000 request. Income $50,000. DTI 120%. Multiple defaults and 5 bankruptcies.", 
        True, 2000000.0, 120.0
    ),
    (
        "Debt consolidation for $18,000. Income $85,000. DTI 25%. 36 months, 7% interest.", 
        False, 18000.0, 25.0
    ),
    (
        "Business expansion $100,000 at 25% interest. $3,500 monthly installment. Revenue $15,000. DTI 95%. 4 derogatory records. 60 months.", 
        True, 100000.0, 95.0
    ),
    (
        "Auto loan $30,000. Income $90,000. DTI 18%. Term 60 months, 5% interest. Mortgage owner.", 
        False, 30000.0, 18.0
    )
]

@pytest.mark.parametrize("raw_doc, expects_interruption, expected_loan, expected_dti", GOLDEN_CASES)
def test_agent_trajectories(agent_graph, raw_doc, expects_interruption, expected_loan, expected_dti):
    config = {"configurable": {"thread_id": f"test_thread_{expected_loan}"}}
    initial_state = {"raw_document": raw_doc}

    agent_graph.invoke(initial_state, config)
    current_state = agent_graph.get_state(config)

    extracted = current_state.values.get("extracted_features", {})
    assert extracted is not None, "Extraction payload is completely missing."

    schema_validation = CreditFeaturesSchema(**extracted)
    assert schema_validation.loan_amnt == expected_loan, f"Hallucination: Expected loan {expected_loan}, got {schema_validation.loan_amnt}"
    assert schema_validation.dti == expected_dti, f"Hallucination: Expected DTI {expected_dti}, got {schema_validation.dti}"

    if expects_interruption:
        assert current_state.next and current_state.next[0] == "human_review_node", \
            f"Failed to route high-risk profile to human review. Current pending node: {current_state.next}"
        
        prediction = current_state.values.get("risk_prediction")
        assert prediction == 1, f"ML API incorrectly scored a catastrophic profile as safe (prediction: {prediction})."
    else:
        assert not current_state.next, "Graph inappropriately paused for a safe profile."
        assert "underwriting_memo" in current_state.values, "Synthesizer failed to generate the final memo."