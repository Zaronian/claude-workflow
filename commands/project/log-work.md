# Log Work Command (Manual Override)

Work logs are written automatically by Claude at every checkpoint and at session end (one file per project per day). This command exists for reviewing, adjusting, or supplementing an auto-generated entry.

## Instructions

When the user runs `/log-work`:

### 1. Check for Existing Entry

Look for an auto-generated work log entry from today. All work logs live in the practice's KB folder regardless of which business the work was for:
- `~/Knowledge-Base/lightswitch/work-logs/YYYY-MM-DD-*.md`

If found, read it and present a summary to the user.

### 2. If Entry Exists → Review & Adjust

Show the user the key fields and ask if anything needs updating:
- Time estimates (manual hours, Claude hours)
- Strategic impact section
- Anything missing or inaccurate

Make requested changes directly to the file.

### 3. If No Entry Exists → Generate One

If no auto-generated entry exists for today's session:

**Determine entity** from recent file paths or ask:
- Burn App
- Lightswitch Labs
- V School
- Smash Creative
- Volley

**Ask 2-3 brief questions:**
- What was accomplished this session?
- How long would this have taken manually? (for time-saved calculation)
- What does getting this done unlock for the business? (strategic impact)

**Write the entry** following `_system/Templates/work-log-entry-template.md` to:
```
~/Knowledge-Base/lightswitch/work-logs/YYYY-MM-DD-[slug].md
```
(name the business inside the entry), then commit and push to main.

### 4. Confirmation

After saving or updating, confirm:
- Where the entry is saved
- Summary of key metrics (hours saved, dollar value)
- Suggest `/case-study` if enough entries have accumulated

## Rate Tiers

- **$35/hr** — Research, admin, documentation, planning, strategy
- **$75/hr** — Coding, development, technical implementation, debugging
