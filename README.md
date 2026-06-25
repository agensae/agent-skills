# agent-skills

A collection of our public agent skills.

## Available Skills

Each listed skill is a self-contained agent skill. The skill directory contains
its `SKILL.md` instructions and any supporting files.

### Analysis

#### Audit Claim Timelines (`audit-claim-timelines`)

Use this when a requirement, policy, example, or finding appears to have changed
over time and you need to know whether it is a real contradiction, a resolved
correction, or an active flip-flop.

**Use it to**
- **Check for back-and-forth change** - You suspect a rule may have changed from
  `A -> B -> A`, or kept switching such as `A -> B -> A -> B`, and need evidence.
- **Verify a one-time conflict or replacement** - You found two versions that
  seem to disagree and need to know whether the older rule was only replaced or
  later came back.
- **Find current source conflicts** - You need to check whether two current
  documents still say different things about the same rule.
- **Validate a finding before applying it** - You have an old finding or review
  note and need to make sure following it will not undo newer guidance.
- **Check for a weaker rule over time** - You suspect the wording became less
  strict and need to know whether the requirement really changed or was only
  rephrased.
- **Confirm an old issue is resolved** - You need to verify that the documents
  now agree, so an old finding can be closed or ignored.
- **Detect old behavior leaking back in** - You need to check whether old,
  removed, or compatibility-only behavior is being treated as current again.
- **Confirm cleanup is complete** - After cleanup, you need to check the
  documents and history, then confirm that no important conflicts remain.

**What you get**
- A timeline that shows what each source said, when it said it, and where the
  evidence is.
- Clear labels for claims that mean the same thing, even when the wording is
  different.
- A plain result that says whether the history shows back-and-forth changes,
  slow weakening, a replaced claim, a live conflict, a resolved issue, or no
  important change.
- A next step, such as updating the source of truth, closing an old finding, or
  avoiding a stale fix.

**Not for**
- Summarizing Git history when you do not need to compare the meaning of a
  claim, rule, policy, or requirement.
- Copyediting or wording review when the expected behavior stayed the same.

**Skill path:** `analysis/audit-claim-timelines`

### Codex

#### Codex Thread Logs (`codex-thread-logs`)

Use this when the source of truth is a Codex session history and you need an
evidence-backed explanation, decision, or reusable workflow from that history.

**Primary use cases**
1. **Thread outcome audits** - Check whether a completed thread's final answer
   was supported by the transcript evidence.
2. **Blocked or failed run diagnosis** - Explain why a thread stopped, failed,
   or reported `BLOCKED`, and identify what remains to be done.
3. **Automation and integration incident analysis** - Reconstruct odd behavior
   around PRs, labels, API calls, sync jobs, appliers, or merge queues.
4. **Agent behavior and claim verification** - Prove or disprove claims about
   what an agent read, ran, changed, skipped, or reverted.
5. **Multi-agent and orchestrator review** - Inspect parent, child, reducer, and
   orchestrator behavior across coordinated agent work.
6. **Environment and tooling friction investigation** - Diagnose failures that
   look like sandbox, filesystem, shell, approval, credential, or macOS privacy
   problems.
7. **Workflow extraction and reuse** - Mine prior threads for a reusable prompt,
   corrected plan, new skill, or recurring process pattern.

**What you get**
- A concise, line-referenced timeline of the relevant session evidence.
- A clear separation between what happened, what the agent claimed, and what the
  user still needs to decide or do.
- A small evidence bundle that can support a review verdict, fix plan,
  orchestrator prompt, or new skill.

**Not for**
- General application logs or code debugging unrelated to Codex sessions.
- Process-quality scorecards by itself; pair it with an evaluation rubric when
  you need a verdict or score.

**Skill path:** `codex/codex-thread-logs`
