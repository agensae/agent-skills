# agent-skills

A collection of our public agent skills.

## Available Skills

Each listed skill is a self-contained agent skill. The skill directory contains
its `SKILL.md` instructions and any supporting files.

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
