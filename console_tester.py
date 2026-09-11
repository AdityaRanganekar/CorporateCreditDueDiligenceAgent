from src.graph.workflow import compile_graph
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def run_local_test():
    graph = compile_graph()

    config = {"configurable": {"thread_id": "local_test_1"}}

    initial_state = {
        "raw_document": "The applicant is requesting a $12,000 loan for home improvement with a 36-month term at 5.5% interest. The monthly installment is $362. They have a strong annual income of $150,000, a highly favorable DTI of 12%, zero bankruptcies, and zero public derogatory records. They have been at their current employer for 10+ years and own their home with an active mortgage."
    }

    print("\n--- STARTING PIPELINE ---")

    for event in graph.stream(initial_state, config, stream_mode="updates"):
        print(f"Node Executed: {list(event.keys())[0]}")

    current_state = graph.get_state(config)

    if current_state.next:
        print("\n--- PIPELINE INTERRUPTED ---")
        print(f"Pending Node: {current_state.next[0]}")

        extracted = current_state.values.get("extracted_features", {})
        risk_prob = current_state.values.get("risk_probability")

        print("\n--- HUMAN REVIEW REQUIRED ---")
        print(f"Risk Probability: {risk_prob}")
        print(f"Extracted Features: {extracted}")

        approval = input("\nDo you approve resuming the graph? (yes/no): ")

        if approval.lower() == "yes":
            print("\n--- RESUMING PIPELINE ---")
            for event in graph.stream(None, config, stream_mode="updates"):
                print(f"Node Executed: {list(event.keys())[0]}")
        else:
            print("\nExecution aborted by human.")
            return

    print("\n--- FINAL RESULTS ---")
    final_state = graph.get_state(config)
    memo = final_state.values.get("underwriting_memo", "No memo generated.")
    
    if memo != "No memo generated.":
        try:
            output_dir = "memos"
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"{output_dir}/credit_memo_{timestamp}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(memo)
            print(f"Successfully saved full output to {filename}!")
        except Exception as e:
            print(f"Failed to save memo to file: {e}")

    print("\nGenerated Memo Preview:")
    print("-" * 40)
    print(memo[:500] + "..." if len(memo) > 500 else memo)
    print("-" * 40)

if __name__ == "__main__":
    run_local_test()