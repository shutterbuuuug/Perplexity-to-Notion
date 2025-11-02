# Perplexity-to-Notion Automation Experiment Documentation

## Overview

This documentation captures the scope, troubleshooting, and final analysis of attempting to automate the export of Perplexity AI search results to Notion, using API integrations, webhook servers, and desktop workflows.

---

## Interaction Timeline

- Initial goal: Build an end-to-end pipeline to automate data collection and export from Perplexity to Notion using their respective APIs, terminal tools, and Mac automations.
- Multiple steps: GitHub repo management, Notion token migration, Python and shell script installs, webhook deployment, API and UI integration attempts.

---

## Major Roadblocks

1. **Perplexity Share URL Limitation**
    - Perplexity's "Share" function outputs dynamic `/search/...` URLs which are **not** public endpoints or persistent threads.
    - Automation tools and API fetches expect a `/share/...` or `/thread/...` style link, resulting in frequent 404 errors (`API request failed: 404 - No content to export`).

2. **Notion API Token Migration & Validation**
    - Notion switched token formats from `secret_...` to `ntn_...`, which required patching validation logic in the setup scripts.
    - Once resolved, Notion integration worked, but exposed downstream API structure issues.

3. **No GUI for Automation**
    - The automation tool includes only terminal interactive mode and API endpoints—no Mac app or browser UI for easy sharing/export.

4. **API Destination Filter Error**
    - Manual export to Notion database failed due to a filter parameter mismatch:  
    ```
    body.filter.value should be `"page"` or `"data_source"`, instead was `"database"`.
    No destination selected
    ```
    - Notion API expects `"page"` or `"data_source"`; code sent `"database"` due to outdated or incorrect implementation.

---

## Actual Results

- **What Worked**
    - Manual workflows:  
        - Exporting Perplexity search result as static files (PDF, Markdown, DOCX) using built-in export tools.
        - Dragging and dropping or importing these files into Notion as attachments or via Markdown conversion.
    - Terminal interactive mode reliably guides manual entry and file-based results.

- **What Failed**
    - All direct attempts to export live Perplexity searches via API or webhook, due to lack of supported endpoints and filter errors.
    - Any automation based on `/search/...` links failed (404).
    - Manual text input in interactive mode also failed to select a database destination due to Notion API filter logic (`400 Bad Request`).


---

## Recommendations for Future Automation Attempts

- Build fallback/manual workflows for dynamic/non-exportable data.
- Patch code to match up-to-date API requirements (including filter values and token formats).
- Encourage clarity in user error messages—show users how to recover when automation breaks.

---

## Conclusion

End-to-end automation is only possible when both source and destination offer compatible, static, and public data endpoints.  
When restricted by platform API limits, the best practice is to guide users into efficient manual workflows, and always document roadblocks and technical limitations for future improvements.

---
