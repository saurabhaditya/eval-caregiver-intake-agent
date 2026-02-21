# Hook Up Your Existing Caregiver Intake Agent

This guide shows how to connect a running caregiver intake agent to the eval framework so it can be evaluated against all 15 scenarios.

## The Interface You Must Implement

Your agent adapter must subclass `AgentBase` and implement one method:

```python
from eval_caregiver.agent.base import AgentBase, AgentOutput

class AgentBase(ABC):
    @abstractmethod
    def run_scenario(self, scenario: TestScenario) -> AgentOutput:
        """Run the agent on a given test scenario and return its output."""
        ...
```

`AgentOutput` is a dataclass with three fields:

```python
@dataclass
class AgentOutput:
    transcript: ConversationTranscript   # The conversation that happened
    intake_record: StructuredIntakeRecord # Structured data the agent extracted
    action_log: AgentActionLog           # Actions the agent took
```

## What Each Scenario Provides

Each `TestScenario` gives your adapter:

| Field | Type | Purpose |
|---|---|---|
| `scenario_id` | `str` | Unique ID like `"compliance_cpr_missing"` |
| `name` | `str` | Human-readable name |
| `description` | `str` | What the scenario tests |
| `caregiver_setup` | `dict` | Simulated caregiver state (e.g. `{"cpr_status": "missing"}`) — use this to configure your agent's input |
| `expected_compliance_gaps` | `list[str]` | What the agent should find (used by graders, not your agent) |
| `expected_geo_concerns` | `list[str]` | Geo concerns the agent should flag (used by graders) |
| `grader_names` | `list[str]` | Which graders will evaluate the output |

## What You Must Return

**1. `ConversationTranscript`** — the actual conversation between your agent and the simulated caregiver:

```python
ConversationTranscript(
    scenario_id="compliance_cpr_missing",
    turns=[
        ConversationTurn(role="agent", content="Welcome! Let me review...", turn_number=1),
        ConversationTurn(role="caregiver", content="Sure, I have my...", turn_number=2),
        # ... all turns
    ],
)
```

**2. `StructuredIntakeRecord`** — the structured data your agent extracted from the conversation:

```python
StructuredIntakeRecord(
    caregiver=CaregiverProfile(
        caregiver_id="cg-001",
        full_name="Jane Smith",
        email="jane.smith@example.com",
        phone="555-0101",
        years_experience=3,
        specialties=["elderly care"],
        compliance=[
            ComplianceRecord(item_name="Background Check", status="valid", expiration_date=date(2026, 6, 15)),
            ComplianceRecord(item_name="CPR Certification", status="missing"),
        ],
        geo_preferences=GeoPreferences(preferred_zones=["zone-a"], max_travel_minutes=30),
    ),
    compliance_gaps=["CPR Certification"],          # gaps your agent identified
    remediation_actions=["Schedule CPR class"],      # actions your agent offered
    geo_concerns=[],                                 # geo issues your agent flagged
    safe_area_suggestions=[],                        # safe zones your agent suggested
    overall_status="needs_review",                   # "complete" | "incomplete" | "needs_review"
)
```

**3. `AgentActionLog`** — what your agent did during the conversation:

```python
AgentActionLog(
    scenario_id="compliance_cpr_missing",
    actions=["Reviewed compliance records", "Identified missing CPR", "Offered scheduling"],
    compliance_items_checked=["Background Check", "CPR Certification"],
    safety_map_consulted=False,
    scheduling_offered=True,
    remediation_steps_offered=["Schedule CPR certification class"],
)
```

## Implementation Template

Create `src/eval_caregiver/agent/live_agent.py`:

```python
"""Adapter that connects your running agent to the eval framework."""

from __future__ import annotations

import os
from datetime import date

from eval_caregiver.agent.base import AgentBase, AgentOutput
from eval_caregiver.schemas.caregiver import (
    CaregiverProfile,
    ComplianceRecord,
    GeoPreferences,
    StructuredIntakeRecord,
)
from eval_caregiver.schemas.conversation import (
    AgentActionLog,
    ConversationTranscript,
    ConversationTurn,
)
from eval_caregiver.schemas.scenarios import TestScenario


class LiveIntakeAgent(AgentBase):
    """Adapter for your real caregiver intake agent."""

    def __init__(self):
        # TODO: Initialize your agent client here.
        # Examples:
        #   self.client = MyAgentClient(api_key=os.environ["AGENT_API_KEY"])
        #   self.agent_url = os.environ["AGENT_URL"]
        pass

    def run_scenario(self, scenario: TestScenario) -> AgentOutput:
        # Step 1: Convert scenario.caregiver_setup into your agent's input format.
        # The caregiver_setup dict contains scenario-specific config like:
        #   {"cpr_status": "missing"}
        #   {"preferred_zones": ["zone-a"], "excluded_zones": ["zone-b", ...]}
        #   {"desired_hourly_rate": 32, "minimum_weekly_hours": 35}
        agent_input = self._build_agent_input(scenario)

        # Step 2: Run your agent and collect the conversation.
        # This is where you call your running agent — via API, SDK, subprocess, etc.
        raw_result = self._call_agent(agent_input)

        # Step 3: Parse the conversation into ConversationTranscript.
        transcript = self._parse_transcript(scenario.scenario_id, raw_result)

        # Step 4: Extract structured intake data from your agent's output.
        intake_record = self._parse_intake_record(raw_result)

        # Step 5: Build the action log from your agent's internal state or output.
        action_log = self._parse_action_log(scenario.scenario_id, raw_result)

        return AgentOutput(
            transcript=transcript,
            intake_record=intake_record,
            action_log=action_log,
        )

    def _build_agent_input(self, scenario: TestScenario) -> dict:
        """Convert scenario setup into your agent's expected input format."""
        # TODO: Map scenario.caregiver_setup to your agent's API format.
        # Example:
        #   return {
        #       "caregiver_profile": scenario.caregiver_setup,
        #       "scenario_description": scenario.description,
        #   }
        raise NotImplementedError

    def _call_agent(self, agent_input: dict) -> dict:
        """Call your running agent and return its raw response."""
        # TODO: Replace with your agent call. Examples:
        #
        # HTTP API:
        #   resp = requests.post(f"{self.agent_url}/intake", json=agent_input)
        #   return resp.json()
        #
        # Python SDK:
        #   return self.client.run_intake(agent_input)
        #
        # Anthropic tool-use agent:
        #   messages = self.client.messages.create(...)
        #   return parse_tool_calls(messages)
        raise NotImplementedError

    def _parse_transcript(self, scenario_id: str, raw: dict) -> ConversationTranscript:
        """Parse your agent's conversation log into ConversationTranscript."""
        # TODO: Map your agent's message format to ConversationTurn objects.
        # Example:
        #   turns = []
        #   for i, msg in enumerate(raw["messages"], 1):
        #       turns.append(ConversationTurn(
        #           role="agent" if msg["sender"] == "bot" else "caregiver",
        #           content=msg["text"],
        #           turn_number=i,
        #       ))
        #   return ConversationTranscript(scenario_id=scenario_id, turns=turns)
        raise NotImplementedError

    def _parse_intake_record(self, raw: dict) -> StructuredIntakeRecord:
        """Extract structured intake data from your agent's output."""
        # TODO: Map your agent's structured output to StructuredIntakeRecord.
        # The graders check these fields:
        #   - compliance_gaps: list of string names of missing/expired items
        #   - remediation_actions: list of actions the agent offered
        #   - geo_concerns: list like ["over_restricted_zones", "limited_assignment_availability"]
        #   - safe_area_suggestions: list like ["Zone B (low risk)"]
        raise NotImplementedError

    def _parse_action_log(self, scenario_id: str, raw: dict) -> AgentActionLog:
        """Build action log from your agent's output or internal state."""
        # TODO: Map your agent's action history. The graders check:
        #   - compliance_items_checked: which items the agent reviewed
        #   - safety_map_consulted: bool — did the agent look at safety data?
        #   - scheduling_offered: bool — did the agent offer to schedule something?
        #   - remediation_steps_offered: what remediation was proposed
        raise NotImplementedError
```

## Wire It Into the CLI

Edit `src/eval_caregiver/runner/cli.py` line 71 — replace `MockAgent()` with your agent:

```python
# Before:
agent = MockAgent()

# After:
from eval_caregiver.agent.live_agent import LiveIntakeAgent
agent = LiveIntakeAgent()
```

Or add a `--live` flag:

```python
parser.add_argument("--live", action="store_true", help="Use live agent instead of mock")

# Then in main():
if args.live:
    from eval_caregiver.agent.live_agent import LiveIntakeAgent
    agent = LiveIntakeAgent()
else:
    agent = MockAgent()
```

## Run the Evaluation

```bash
# With mock agent (validation):
uv run eval-runner --scorecard --no-model-graders

# With your live agent:
export AGENT_API_KEY=...             # your agent's credentials
export ANTHROPIC_API_KEY=sk-ant-...  # for model-based graders
uv run eval-runner --live --scorecard

# Run only eligibility scenarios against your live agent:
uv run eval-runner --live -c eligibility_improvement_cases --scorecard

# Fast run (skip LLM graders):
uv run eval-runner --live --scorecard --no-model-graders
```

## What the Graders Check

Your agent's output is graded automatically:

| Grader | Checks | Key Fields It Reads |
|---|---|---|
| `compliance_gap_detection` | Found all expected gaps | `intake_record.compliance_gaps` vs `scenario.expected_compliance_gaps` |
| `compliance_remediation` | Offered remediation | `intake_record.remediation_actions`, `action_log.scheduling_offered`, `action_log.remediation_steps_offered` |
| `geo_restriction_detection` | Flagged over-restriction, suggested alternatives | `intake_record.geo_concerns`, `intake_record.safe_area_suggestions`, `action_log.safety_map_consulted` |
| `scheduling_helpfulness` | Conversation quality (LLM judge) | `transcript.full_text` |
| `safe_area_suggestion_quality` | Safety data referenced (LLM judge) | `transcript.full_text` |

## Tips

- Start with one scenario: `uv run eval-runner --live -c compliance_missing_cases --scorecard --no-model-graders`
- The `caregiver_setup` dict is your scenario input — it tells you what simulated caregiver state to feed your agent
- The `expected_*` fields are for graders only — your agent should discover gaps on its own, not read them from the scenario
- If your agent doesn't produce an explicit action log, you can infer it from the conversation (e.g., if the transcript mentions "I'll schedule a class," set `scheduling_offered=True`)

---

## Boundaries Between Eval and Agent

The eval framework is a **black-box tester**. It feeds inputs, collects outputs, and judges them. The agent is the **system under test**. It should have no awareness that it's being evaluated.

The moment concepts leak across this boundary, your eval stops measuring real agent quality and starts measuring "how well the agent games the eval."

### Dependency Graph

```
eval_framework  ◄──depends on──  adapter  ──depends on──►  agent
      │                             │                         │
      │ NEVER imports from agent    │ imports from both       │ NEVER imports from eval
      │ NEVER reads agent config    │ translates between      │ NEVER reads scenarios
      │ NEVER calls agent directly  │ the two systems         │ NEVER sees expected answers
```

- **Eval framework** depends on nothing external. It defines schemas, loads JSON, runs graders.
- **Agent** depends on nothing eval-related. It takes caregiver situations, has conversations, produces its own structured output.
- **Adapter** is the only thing that touches both. It lives outside both codebases (or in a thin integration layer).

### What Must NOT Cross Over

#### 1. Expected answers must never reach the agent

| Concept | Lives in | Must NOT reach |
|---|---|---|
| `expected_compliance_gaps` | Scenario JSON | Agent's prompt or context |
| `expected_geo_concerns` | Scenario JSON | Agent's prompt or context |
| `grader_names` | Scenario JSON | Agent (it shouldn't know what's being graded) |
| Grader pass/fail thresholds | Grader code | Agent's decision logic |

If the agent sees `expected_compliance_gaps: ["CPR Certification"]`, it can just echo that back without actually reasoning about the caregiver's situation. The eval becomes a tautology.

**In the adapter**: Pass `scenario.caregiver_setup` to the agent but **strip** `expected_*` fields, `grader_names`, and `required`.

#### 2. Grader rubrics must not inform agent prompting

| Concept | Lives in | Must NOT reach |
|---|---|---|
| Grader scoring criteria | `graders/code_based/*.py` | Agent's system prompt |
| Model-based rubric criteria | `graders/model_based/*.py` | Agent's system prompt |
| Quality gate thresholds | `quality_gates.py` | Agent config |
| Field-level grading logic | e.g. "recall >= 0.95" | Agent behavior |

If your agent's system prompt says "always set `scheduling_offered` to true and list remediation steps," it's not demonstrating real capability — it's teaching to the test.

#### 3. Eval schema is a contract, not the agent's data model

The agent should have **its own** internal data models. The adapter translates between them.

```
Agent's native model          Adapter              Eval schema
─────────────────         ───────────────      ─────────────────
agent.PatientRecord   →   _parse_intake()  →   StructuredIntakeRecord
agent.ChatHistory     →   _parse_transcript()→  ConversationTranscript
agent.StepLog         →   _parse_actions() →   AgentActionLog
```

If the agent imports `eval_caregiver.schemas` directly and constructs its output to match, you're coupling the agent to the eval. Change the eval schema, agent breaks. Worse — the agent developer starts thinking in eval-schema terms instead of "what does the caregiver actually need."

#### 4. Mock responses are eval-only test fixtures

| Concept | Lives in | Must NOT reach |
|---|---|---|
| Mock agent responses (`data/responses/`) | Eval framework | Agent training data or few-shot examples |
| Mock conversation patterns | Eval JSON files | Agent prompt engineering |
| Scenario descriptions | Eval JSON files | Agent's runtime context |

The mock responses are *ideal outputs* that define what a perfect agent would do. If you use them as few-shot examples in the agent's prompt, the agent learns to mimic the eval's expectations rather than developing genuine capability.

#### 5. Agent internals must not leak into graders

| Concept | Lives in | Must NOT reach |
|---|---|---|
| Agent's prompt templates | Agent codebase | Grader logic |
| Agent's tool call format | Agent codebase | Grader expectations |
| Agent's retry/fallback logic | Agent codebase | Eval assumptions |
| Agent's LLM provider/model | Agent config | Grader behavior |

Graders should evaluate **what** the agent produced, not **how** it produced it. If a grader checks "did the agent use the `check_compliance` tool," you're testing implementation, not outcomes. A different agent architecture that achieves the same result would fail.

### Litmus Tests

Before making a change, ask:

| Question | If yes... |
|---|---|
| Could the agent pass this eval without actually being good at intake? | You've leaked grader logic into the agent |
| Would changing the eval schema require changing the agent? | The agent is coupled to eval internals |
| Does the agent behave differently when it knows it's being evaluated? | The eval isn't measuring real behavior |
| Does a grader assume a specific agent architecture? | The grader is testing implementation, not outcomes |
| Are mock responses used anywhere in agent training? | You're teaching to the test |

The strongest eval is one where the agent developer has **never read the grader code** and the eval developer has **never read the agent's prompts**.
