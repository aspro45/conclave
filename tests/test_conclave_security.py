"""Executable Conclave authorization, review and settlement tests."""

import json
from pathlib import Path


CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "conclave_v2.py")


def _reviewed_debate(contract, vm, against):
    debate_id = contract.draft_debate(
        "0x" + against.hex(),
        "Should the protocol adopt the proposed release policy?",
        "The FOR side wins only if two independent official sources support the policy.",
        "https://example.com/policy",
        "0",
    )
    contract.add_position(str(debate_id), "FOR policy", "The official roadmap supports adoption.", "https://example.org/roadmap")
    vm.mock_llm(
        r"adjudicating a structured public debate",
        json.dumps({
            "outcome": "met",
            "confidenceBps": 8200,
            "winnerBps": 8500,
            "summary": "The official sources support the FOR position.",
            "rationale": "The policy and roadmap are consistent.",
            "riskFlags": [],
        }),
    )
    contract.judge_debate_with_genlayer(str(debate_id))
    contract.open_challenge_window(str(debate_id))
    return debate_id


def test_standard_and_judgement_are_authorized(deploy, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = deploy(CONTRACT)
    debate_id = contract.draft_debate(
        "0x" + direct_bob.hex(),
        "A public motion",
        "Resolve from official public evidence.",
        "https://example.com/source",
        "0",
    )

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("admin_only"):
        contract.set_conclave_standard("Attacker-controlled standard")

    direct_vm.sender = bytes.fromhex("11" * 20)
    with direct_vm.expect_revert("debate_operator_only"):
        contract.judge_debate_with_genlayer(str(debate_id))


def test_challenge_changes_outcome_and_settlement_waits(deploy, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = deploy(CONTRACT)
    debate_id = _reviewed_debate(contract, direct_vm, direct_bob)

    direct_vm.sender = direct_bob
    challenge_id = contract.submit_challenge(
        str(debate_id),
        "The roadmap was superseded by a final policy notice.",
        "https://example.net/final-notice",
    )

    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("open_filing_blocks_settlement"):
        contract.settle(debate_id)
    direct_vm.mock_llm(
        r"resolving a Conclave V2 challenge",
        json.dumps({
            "ruling": "accepted",
            "revisedOutcome": "not_met",
            "confidenceDeltaBps": -900,
            "reason": "The final notice supersedes the roadmap.",
            "riskFlags": ["SUPERSEDED_SOURCE"],
        }),
    )
    contract.resolve_challenge_with_genlayer(str(debate_id), challenge_id)
    record = json.loads(contract.get_debate_record(str(debate_id)))
    assert record["outcome"] == "not_met"
    with direct_vm.expect_revert("settlement_not_mature"):
        contract.settle(debate_id)

