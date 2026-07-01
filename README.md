# Conclave

Evidence-weighted debates with a recorded decision path.

Conclave treats a debate like a structured case. Each side can add positions and sources, GenLayer judges the argument against the evidence, and the contract keeps challenge and appeal paths for contested outcomes. The goal is a public decision room where the reasoning trail is inspectable after the vote.

## Where To Review It

| Surface | URL |
| --- | --- |
| App | https://conclave-github.vercel.app |
| GitHub | https://github.com/aspro45/conclave |
| Contract | https://explorer-studio.genlayer.com/contracts/0x44ccfCdeb1e9667C8548E051eDcf6D734c3fBA59 |

## Chain Details

- Network: GenLayer Studionet
- Chain ID: `61999`
- Contract: `0x44ccfCdeb1e9667C8548E051eDcf6D734c3fBA59`
- Deploy tx: [`0xbb0fae532cd8410e970abe6a3c97416ab7dbe0e506bd99812b9cf97be68b06b0`](https://explorer-studio.genlayer.com/tx/0xbb0fae532cd8410e970abe6a3c97416ab7dbe0e506bd99812b9cf97be68b06b0)
- Deployed: `2026-06-23T20:12:44.928Z`
- Smoke writes: `19`

## Contract Design

The main source is `contracts/conclave_v2.py` at 39,903 bytes. It includes debate records, argument records, evidence links, status-indexed reads and party views. GenLayer is used for web-source review and validator-comparative judgement.

Important reads include `get_debate_count`, `get_debate`, `get_argument_count`, `get_argument`, `get_debate_record`, `get_recent_debates`, `get_debates_by_status` and `get_party_debates`.

## Case Flow

1. Set the debate standard.
2. Draft a debate.
3. Add a position for each side.
4. Attach evidence sources.
5. Open deliberation.
6. Run GenLayer judgement.
7. Allow challenge or appeal.
8. Archive the debate with its final record.

## Verified Transactions

| Action | Explorer |
| --- | --- |
| `set_conclave_standard` | [0xef60d263...d0f512](https://explorer-studio.genlayer.com/tx/0xef60d263dd657cdf7ada923c10e5af714e9ad32a9eb7cef785da565d76d0f512) |
| `draft_debate` | [0x9dd574e4...029bfc](https://explorer-studio.genlayer.com/tx/0x9dd574e454f12439071a3e3a3da96537883a2a515e75ef3920b54d38f1029bfc) |
| `add_position_for` | [0xd00676a9...1f1e94](https://explorer-studio.genlayer.com/tx/0xd00676a9ec9b418499828e96cb294294403f30f43d42bfa73685e62e431f1e94) |
| `add_position_against` | [0xdb1edea4...ad2adb](https://explorer-studio.genlayer.com/tx/0xdb1edea4b5505efa34ee8f448cbdb41390283cd6299f9830f8a410e578ad2adb) |
| `open_deliberation` | [0x00872d59...9473c1](https://explorer-studio.genlayer.com/tx/0x00872d590f1098f18213c1c081d32643ee1aae3c90e5c192fcd1dff8089473c1) |
| `judge` | [0x8f08ad56...652d73](https://explorer-studio.genlayer.com/tx/0x8f08ad567fb89d26c3f5076d5a24869801afd86addee458d38dab51e62652d73) |

## Local Preview

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Safe To Publish

Contract source, frontend files and public deployment records are intended for GitHub and Vercel. Private keys, vault files, `.env` files and `.vercel/` state are local-only.
