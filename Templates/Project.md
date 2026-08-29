---
date: <% tp.date.now("YYYY-MM-DD") %>
type: project
tags:
  - project
ai-first: true
status: active
job:
---

# <% tp.file.title %>

## For future agent

Project note. Captures overview, architecture, key decisions, and related tasks. Pull this when reasoning about the project's direction, prior decisions, or current scope.

## Overview
<% tp.file.cursor() %>

## Architecture


## Key Decisions


## Links


## Related Tasks

```dataview
TABLE WITHOUT ID file.link AS "Task", status AS "Status"
FROM "Tasks"
WHERE contains(file.outlinks, this.file.link)
SORT date DESC
```

## Recent Activity

```dataview
LIST FROM "Daily"
WHERE contains(file.outlinks, this.file.link)
SORT date DESC
LIMIT 5
```
