# Backlog Management Guide

> **Purpose:** Guidelines for managing and maintaining the project backlog  
> **Target Audience:** Project team members, product owner, scrum master

---

## Table of Contents

- [Overview](#overview)
- [Backlog Structure](#backlog-structure)
- [Backlog Item Lifecycle](#backlog-item-lifecycle)
- [Prioritization Framework](#prioritization-framework)
- [Estimation Guidelines](#estimation-guidelines)
- [Refinement Process](#refinement-process)
- [Sprint Planning](#sprint-planning)
- [Best Practices](#best-practices)

---

## Overview

The project uses a hierarchical backlog structure to manage work:

1. **Product Backlog** (`PRODUCT_BACKLOG.md`) - Master list of all work items
2. **Sprint Backlogs** (`sprints/sprint-N.md`) - Work committed for specific sprints
3. **GitHub Issues** - Individual trackable items linked to backlog

### Key Principles

- **Single Source of Truth:** Product backlog is the definitive source
- **Always Prioritized:** Items are ordered by value and urgency
- **Living Document:** Backlog evolves based on learning and feedback
- **Transparent:** Everyone can see and understand the backlog

---

## Backlog Structure

### Hierarchy

```
Epic (21+ points)
  └── User Story (3-13 points)
      └── Task (1-8 points)
          └── Subtask (< 1 hour)
```

### Item Format

Each backlog item includes:

```markdown
#### BACK-XX: [Title]
- **Priority:** P0/P1/P2/P3
- **Story Points:** X
- **Status:** ⬜/🚧/✅/⏸️/❌
- **Assignee:** [Name]
- **Dependencies:** [Other items]

**Description:**
[What needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Technical Notes:**
[Implementation details]
```

### Phases

Items are organized into phases:
- **Phase 1:** Core Functionality (MVP)
- **Phase 2:** Agent System
- **Phase 3:** UI/UX Polish
- **Phase 4:** Evaluation & Documentation
- **Future:** Post-launch enhancements

---

## Backlog Item Lifecycle

### 1. Creation
- Item identified through:
  - User feedback
  - Technical requirements
  - Bug reports
  - Strategic planning
- Added to appropriate phase/epic
- Given temporary ID: `BACK-TBD`

### 2. Refinement
- Details fleshed out
- Acceptance criteria defined
- Dependencies identified
- Estimated (story points)
- Assigned permanent ID: `BACK-XX`

### 3. Prioritization
- Priority assigned (P0-P3)
- Positioned in backlog order
- Dependencies considered

### 4. Ready for Sprint
- Fully refined
- Acceptance criteria clear
- Dependencies resolved
- Estimated appropriately
- Team understands scope

### 5. In Progress
- Assigned to team member
- Status: 🚧 In Progress
- Tracked in current sprint
- GitHub issue created/updated

### 6. Done
- All acceptance criteria met
- Code reviewed and merged
- Tests passing
- Documentation updated
- Status: ✅ Completed

### 7. Archived
- Moved to completed items
- Removed from active backlog
- Retained for reference

---

## Prioritization Framework

### Priority Levels

#### P0 - Critical
- **Definition:** Must have for system to work
- **Examples:**
  - Core API endpoints
  - Essential validation logic
  - Critical bug fixes
- **Timeline:** Current sprint or next
- **Decision maker:** Product Owner

#### P1 - High
- **Definition:** Important for complete user experience
- **Examples:**
  - Secondary features
  - Performance improvements
  - Important integrations
- **Timeline:** Within current phase
- **Decision maker:** Product Owner with team input

#### P2 - Medium
- **Definition:** Valuable but not essential
- **Examples:**
  - Nice-to-have features
  - UI enhancements
  - Additional documentation
- **Timeline:** Future phases
- **Decision maker:** Team consensus

#### P3 - Low
- **Definition:** Minimal impact on users
- **Examples:**
  - Future enhancements
  - Experimental features
  - Code refactoring
- **Timeline:** Backlog, may not be done
- **Decision maker:** Team decision

### Prioritization Criteria

Use these factors to determine priority:

1. **Business Value**
   - User impact (High/Medium/Low)
   - Stakeholder importance
   - Revenue/cost impact

2. **Dependencies**
   - Blocks other work?
   - Foundation for other features?
   - External deadlines?

3. **Risk**
   - Technical complexity
   - Uncertainty
   - Integration challenges

4. **Effort**
   - Story points
   - Team availability
   - Resource requirements

### MoSCoW Method

Alternative prioritization:
- **Must Have:** P0
- **Should Have:** P1
- **Could Have:** P2
- **Won't Have (this time):** P3

---

## Estimation Guidelines

### Story Points

We use Fibonacci sequence for story points:
- **1:** Trivial (< 2 hours)
- **2:** Simple (2-4 hours)
- **3:** Moderate (4-8 hours)
- **5:** Medium (1 day)
- **8:** Large (2 days)
- **13:** Very large (3-4 days)
- **21+:** Epic (needs breakdown)

### What to Consider

- **Complexity:** How difficult?
- **Effort:** How much work?
- **Uncertainty:** How much is unknown?
- **Dependencies:** What's required?

### Estimation Process

1. **Planning Poker:**
   - Each team member estimates independently
   - Reveal simultaneously
   - Discuss differences
   - Re-estimate until consensus

2. **Reference Stories:**
   - Use completed items as baseline
   - "This is like BACK-10, so probably 5 points"

3. **T-Shirt Sizing (Alternative):**
   - XS, S, M, L, XL
   - Convert to story points later

### Common Pitfalls

❌ **Don't:**
- Estimate in hours directly
- Let one person dominate estimation
- Skip discussion of differences
- Over-analyze (use gut feel)

✅ **Do:**
- Estimate as a team
- Consider all aspects
- Refine estimates as you learn
- Track actual vs. estimated

---

## Refinement Process

### When to Refine

- **Backlog Refinement Meeting:** Weekly, 1 hour
- **Ad-hoc:** As new items emerge
- **Pre-sprint:** Items for next 2-3 sprints

### Refinement Checklist

For each item, ensure:

- [ ] **Clear Description:** Everyone understands what's needed
- [ ] **Acceptance Criteria:** Measurable and testable
- [ ] **Story Points:** Estimated by team
- [ ] **Priority:** Assigned and justified
- [ ] **Dependencies:** Identified and documented
- [ ] **Technical Notes:** Key decisions documented
- [ ] **Size:** Can be completed in one sprint
  - If not, break down into smaller items

### Breaking Down Large Items

If item is > 13 points:

1. **Identify sub-components**
   - What are the logical pieces?
   - Can parts be done independently?

2. **Create child items**
   - Each should deliver value
   - Each should be testable
   - Each should fit in sprint

3. **Link relationships**
   - Document dependencies
   - Maintain traceability

### Refinement Meeting Agenda

1. **Review (10 min)**
   - Changes since last meeting
   - Completed items
   - Emerging needs

2. **Refine Top Items (40 min)**
   - Next 2-3 sprints worth
   - Add details
   - Estimate
   - Discuss questions

3. **Wrap-up (10 min)**
   - Summary of changes
   - Action items
   - Next meeting

---

## Sprint Planning

### Pre-Planning

Before sprint planning meeting:

1. **Backlog Ready**
   - Top items refined
   - Priorities clear
   - Estimates current

2. **Team Capacity Known**
   - Calculate available hours
   - Consider time off, meetings
   - Review velocity

3. **Previous Sprint Reviewed**
   - What was completed?
   - What rolled over?
   - Lessons learned?

### Sprint Planning Meeting

**Part 1: What to build? (1 hour)**

1. **Review Sprint Goal**
   - What will we achieve?
   - How does it align with roadmap?

2. **Select Items**
   - Start from top of backlog
   - Consider priority and dependencies
   - Check capacity
   - Team discusses and commits

3. **Adjust as Needed**
   - Swap items if needed
   - Break down if too large
   - Consider technical constraints

**Part 2: How to build? (1 hour)**

1. **Break Into Tasks**
   - Each item → subtasks
   - Identify technical approach
   - Assign initial owners

2. **Verify Capacity**
   - Sum story points
   - Compare to velocity
   - Adjust if needed

3. **Create Sprint Backlog**
   - Document in `sprints/sprint-N.md`
   - Create GitHub issues
   - Set up tracking

### Sprint Backlog Management

During sprint:

- **Daily Updates**
  - Move items through states
  - Update task completion
  - Flag blockers

- **Sprint Board**
  - To Do
  - In Progress
  - In Review
  - Done

- **No Scope Changes**
  - Sprint backlog is frozen
  - Urgent items go to next sprint
  - Exception: Critical bugs only

---

## Best Practices

### Do's ✅

1. **Keep It Current**
   - Review weekly
   - Remove obsolete items
   - Update priorities

2. **Make It Visible**
   - Everyone knows where to find it
   - Current state always clear
   - Changes communicated

3. **Collaborate**
   - Involve whole team
   - Seek user feedback
   - Consider stakeholder input

4. **Stay Flexible**
   - Adjust based on learning
   - Reprioritize as needed
   - Adapt to change

5. **Focus on Value**
   - Prioritize user impact
  - Deliver working software
   - Validate assumptions

6. **Maintain Quality**
   - Don't rush items
   - Include testing time
   - Allocate for technical debt

### Don'ts ❌

1. **Don't Over-Commit**
   - Be realistic with capacity
   - Leave buffer for unknowns
   - Quality over quantity

2. **Don't Skip Refinement**
   - Poorly defined items cause delays
   - Estimates will be wrong
   - Rework wastes time

3. **Don't Ignore Technical Debt**
   - Allocate time for cleanup
   - Address root causes
   - Prevent future issues

4. **Don't Work in Isolation**
   - Communicate changes
   - Share learnings
   - Ask for help

5. **Don't Forget Documentation**
   - Update as you build
   - Document decisions
   - Help future maintainers

---

## Metrics & Tracking

### Key Metrics

1. **Velocity**
   - Story points completed per sprint
   - Track over time
   - Use for planning

2. **Throughput**
   - Items completed per sprint
   - Trend over time

3. **Cycle Time**
   - Time from start to done
   - Identify bottlenecks

4. **Backlog Health**
   - Age of items
   - Refinement status
   - Priority distribution

### Reviews

**Weekly:**
- Backlog refinement
- Priority check
- Upcoming items ready?

**Sprint End:**
- Velocity calculation
- Completion rate
- Retrospective adjustments

**Monthly:**
- Overall progress vs. roadmap
- Backlog size trend
- Technical debt review

---

## Tools

### Required
- **PRODUCT_BACKLOG.md** - Master backlog
- **GitHub Issues** - Task tracking
- **Sprint files** - Sprint-specific backlogs

### Optional
- **Project Board** - Visual Kanban
- **Burndown Chart** - Progress visualization
- **Roadmap View** - Long-term planning

---

## Templates

### Creating New Sprint

```bash
# Copy template
cp SPRINT_BACKLOG_TEMPLATE.md sprints/sprint-01.md

# Update sprint info
# - Sprint number
# - Dates
# - Goal
# - Selected items
```

### Creating GitHub Issue from Backlog

1. Use issue template: "Feature/Task"
2. Fill in backlog ID
3. Copy acceptance criteria
4. Link to backlog item in description
5. Apply appropriate labels
6. Add to project board

---

## Getting Help

### Questions?

- **Product Owner:** Final decisions on priorities
- **Scrum Master:** Process and facilitation
- **Tech Lead:** Technical feasibility
- **Team:** Collaborative estimation and refinement

### Resources

- [Product Backlog](PRODUCT_BACKLOG.md)
- [Sprint Template](SPRINT_BACKLOG_TEMPLATE.md)
- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [Contributing Guide](docs/CONTRIBUTING.md)

---

## Glossary

- **Backlog:** Ordered list of work items
- **Epic:** Large feature requiring multiple sprints
- **Story Points:** Relative measure of effort/complexity
- **Sprint:** Fixed time period (usually 2 weeks) to complete work
- **Velocity:** Average story points completed per sprint
- **Refinement:** Process of adding detail to backlog items
- **Technical Debt:** Code quality issues that need addressing

---

**Last Updated:** 2026-02-08  
**Version:** 1.0
