# Module: Adapt

**Trigger**: adapt, 换投, 改投, journal adaptation, reformat, 期刊适配, resubmit, change venue, switch journal, format conversion

## Commands

This module does not have a dedicated script. It is an LLM-driven workflow.

## Workflow

1. Read `references/JOURNAL_ADAPTATION_WORKFLOW.md` for the full 4-step process
2. Cross-reference `references/CITATION_STYLES.md` for citation format rules
3. Cross-reference `references/VENUES.md` for venue-specific requirements
4. Cross-reference `references/NUMBER_UNIT_GUIDE.md` for number/unit conventions
5. Cross-reference `references/TABLE_GUIDE.md` for table format requirements

## Details

The adapt module guides a systematic venue-to-venue format conversion:
- Detects current venue from preamble
- Accepts target venue or user-provided journal guidelines (highest priority)
- Generates a diff checklist across 5 dimensions (references, abstract, numbers, figures/tables, layout)
- Applies automated changes with `[ADAPTED: reason]` annotations
- Produces a manual checklist for layout items that cannot be automated

Key constraint: never alter substantive content (arguments, data, conclusions).

Skill-layer response: present the diff checklist, annotated changes, and manual checklist as structured output.
