---
date: <% tp.date.now("YYYY-MM-DD") %>
type: person
tags:
  - person
ai-first: true
role:
company:
relationship_strength:
last_interaction: <% tp.date.now("YYYY-MM-DD") %>
follow_up_date:
contact_email:
location:
---

# <% tp.file.title %>

## For future agent

Person note. Captures role, company, relationship context, what they care about, and how to help each other. Pull this before any interaction with this person or when reasoning about who knows what.

## About
<% tp.file.cursor() %>

## What They Care About


## How We Can Help Each Other


## Notes


---

## Interactions

```dataview
LIST FROM "Daily"
WHERE contains(file.outlinks, this.file.link)
SORT date DESC
LIMIT 15
```
