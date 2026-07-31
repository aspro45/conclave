# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
CONCLAVE - AI-Arbitrated Debates
================================
Anyone opens a motion. Participants argue FOR or AGAINST, optionally citing
evidence. When a debate is concluded, the contract hands both sides to a
validator set under the Equivalence Principle: which side argued more
convincingly on the merits? The ruling is recorded on-chain. No votes, no
brigading - a reasoned verdict.

Debate status: OPEN(0) -> RULED(1)
Winner:        NONE(0) | FOR(1) | AGAINST(2)
Argument side: FOR(1) | AGAINST(2)
"""

from genlayer import *
from dataclasses import dataclass
import json
import typing


OPEN = 0
RULED = 1
W_NONE = 0
W_FOR = 1
W_AGAINST = 2


@allow_storage
@dataclass
class Argument:
    debate_id: u256
    side: u8
    author: Address
    text: str
    evidence_url: str


@allow_storage
@dataclass
class Debate:
    opener: Address
    motion: str
    status: u8
    winner: u8
    rationale: str


class Conclave(gl.Contract):
    debates: DynArray[Debate]
    arguments: DynArray[Argument]

    def __init__(self) -> None:
        pass

    @gl.public.write
    def open_debate(self, motion: str) -> int:
        if len(motion.strip()) == 0:
            raise gl.vm.UserError("a motion is required")
        d = self.debates.append_new_get()
        d.opener = gl.message.sender_address
        d.motion = motion
        d.status = u8(OPEN)
        d.winner = u8(W_NONE)
        d.rationale = ""
        return len(self.debates) - 1

    @gl.public.write
    def argue(self, debate_id: int, side: int, text: str, evidence_url: str) -> None:
        d = self._get(debate_id)
        if d.status != OPEN:
            raise gl.vm.UserError("this debate is closed")
        if side not in (1, 2):
            raise gl.vm.UserError("side must be 1 (for) or 2 (against)")
        if len(text.strip()) == 0:
            raise gl.vm.UserError("an argument is required")
        a = self.arguments.append_new_get()
        a.debate_id = u256(debate_id)
        a.side = u8(side)
        a.author = gl.message.sender_address
        a.text = text
        a.evidence_url = evidence_url

    @gl.public.write
    def conclude(self, debate_id: int) -> None:
        d = self._get(debate_id)
        if d.status != OPEN:
            raise gl.vm.UserError("this debate is already ruled")
        fors = []
        againsts = []
        for a in self.arguments:
            if int(a.debate_id) == debate_id:
                line = a.text.strip()
                if len(a.evidence_url.strip()) > 0:
                    line = line + " [evidence: " + a.evidence_url.strip() + "]"
                if int(a.side) == 1:
                    fors.append(line)
                else:
                    againsts.append(line)
        if len(fors) == 0 or len(againsts) == 0:
            raise gl.vm.UserError("need at least one argument on each side")

        motion = d.motion
        for_block = "\n".join("- " + x for x in fors)
        against_block = "\n".join("- " + x for x in againsts)

        def leader_fn() -> str:
            prompt = (
                f"You are an impartial adjudicator of a structured debate.\n"
                f"MOTION: {motion}\n\n"
                f"ARGUMENTS FOR the motion:\n{for_block}\n\n"
                f"ARGUMENTS AGAINST the motion:\n{against_block}\n\n"
                "Judge strictly on reasoning quality, evidence and rebuttal - not on "
                "the number of arguments. Which side argued more convincingly? "
                'Reply with ONLY JSON: {"winner": "for"} or {"winner": "against"}, '
                'plus a short "reason".'
            )
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            return self._winner_of(leader_res.calldata)[0] == self._winner_of(leader_fn())[0]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        winner, reason = self._winner_of(result)
        d.winner = u8(winner)
        d.rationale = reason[:300]
        d.status = u8(RULED)

    # ------------------------------------------------------------------ views
    @gl.public.view
    def get_debate_count(self) -> int:
        return len(self.debates)

    @gl.public.view
    def get_debate(self, debate_id: int) -> dict:
        d = self._get(debate_id)
        nf = 0
        na = 0
        for a in self.arguments:
            if int(a.debate_id) == debate_id:
                if int(a.side) == 1:
                    nf += 1
                else:
                    na += 1
        return {
            "opener": d.opener.as_hex,
            "motion": d.motion,
            "status": int(d.status),
            "winner": int(d.winner),
            "rationale": d.rationale,
            "for_count": nf,
            "against_count": na,
        }

    @gl.public.view
    def get_argument_count(self) -> int:
        return len(self.arguments)

    @gl.public.view
    def get_argument(self, idx: int) -> dict:
        if idx < 0 or idx >= len(self.arguments):
            raise gl.vm.UserError("no such argument")
        a = self.arguments[idx]
        return {
            "debate_id": int(a.debate_id),
            "side": int(a.side),
            "author": a.author.as_hex,
            "text": a.text,
            "evidence_url": a.evidence_url,
        }

    # -------------------------------------------------------------- internals
    def _get(self, debate_id: int) -> Debate:
        if debate_id < 0 or debate_id >= len(self.debates):
            raise gl.vm.UserError("no such debate")
        return self.debates[debate_id]

    def _winner_of(self, result: typing.Any) -> tuple:
        data = result
        if isinstance(data, str):
            data = self._extract_json(data)
        if not isinstance(data, dict):
            return (W_NONE, "")
        raw = str(data.get("winner", "")).strip().lower()
        reason = str(data.get("reason", ""))
        if raw == "for":
            return (W_FOR, reason)
        if raw == "against":
            return (W_AGAINST, reason)
        return (W_NONE, reason)

    def _extract_json(self, text: str) -> typing.Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (ValueError, TypeError):
                return None
        return None
