# Conclave

Evidence-weighted debates with a recorded decision path.

Conclave treats a debate like a structured case. Each side can add positions and sources, GenLayer judges the argument against the evidence, and the contract keeps challenge and appeal paths for contested outcomes. The goal is a public decision room where the reasoning trail is inspectable after the vote.

## Where To Review It

| Surface | URL |
| --- | --- |
| App | https://tanawo3-conclave.vercel.app |
| GitHub | https://github.com/aspro45/conclave |
| Contract | https://explorer-bradbury.genlayer.com/address/0xAff6205f7d3403Cf434415C9a5e09D67E8644861 |

## Chain Details

- Network: GenLayer Bradbury
- Chain ID: `4221`
- Contract: `0xAff6205f7d3403Cf434415C9a5e09D67E8644861`
- Deploy tx: [`0x7b930009ba8277e2cfc5ae3508e44540289ef2b82ae9d4f4bcf9fc2dc6ec14cf`](https://explorer-bradbury.genlayer.com/tx/0x7b930009ba8277e2cfc5ae3508e44540289ef2b82ae9d4f4bcf9fc2dc6ec14cf)
- Deployed: `2026-07-01T21:09:25.145Z`
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
| `set_conclave_standard` | [0xe121a094...4971da](https://explorer-bradbury.genlayer.com/tx/0xe121a094d80e89dc14e8674ce1ed0c796b874c1388d0f392f74ef006794971da) |
| `draft_debate` | [0xe7aab3c3...7285ef](https://explorer-bradbury.genlayer.com/tx/0xe7aab3c3b081f193fec3278fc82a08caa1138506b8790291418e32fba57285ef) |
| `add_position_for` | [0x71bef6f0...7de92b](https://explorer-bradbury.genlayer.com/tx/0x71bef6f02ee9e6f2f910d006e05fc047670d6d4c83329a1a3f56bc85207de92b) |
| `add_position_against` | [0x13e30d54...13faf3](https://explorer-bradbury.genlayer.com/tx/0x13e30d5457666e51744b10a3439db68e567d5d4a910154d5196c3e9f7813faf3) |
| `open_deliberation` | [0x275d89d7...35b86e](https://explorer-bradbury.genlayer.com/tx/0x275d89d7547acdd192af03df79f165c6fe61f00e45e0adac9b0c81e95535b86e) |
| `judge` | [0x64272929...bd728e](https://explorer-bradbury.genlayer.com/tx/0x642729296cc6171b00c190e6f180f00b398a7c4eb0ba43de296ba8bbd5bd728e) |

## Local Preview

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Safe To Publish

Contract source, frontend files and public deployment records are intended for GitHub and Vercel. Private keys, vault files, `.env` files and `.vercel/` state are local-only.
