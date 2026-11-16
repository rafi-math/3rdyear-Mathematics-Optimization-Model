# Comprehensive Website Fix & Feature Specification (v2)

## 1. Global Themes & Language Toggle
- Dark & Light Mode: Add a persistent theme toggle (sun/moon icon) in the top navigation bar using CSS custom properties. Keep Swiss minimal warm off-white as default light mode, and clean charcoal/off-white for dark mode.
- English & Bangla Toggle: Add an EN | বাংলা toggle switch in the top navigation bar. Translate all navigation links, section headers, buttons, table headers, difficulty labels, rules, and helper text into natural Bangla when toggled.

## 2. Top Header & Typography Cleanup
- Fix Top-Right Toggle (MIN | H): Clarify or move the MIN | H unit toggle into the Calculator section so the top-right header only contains clean global controls (Language toggle + Dark/Light mode toggle).
- Unified Font Family: Use one cohesive, clean Swiss editorial sans-serif font across the entire site (removing the mixed typewriter/monospace body font so headings and body text look unified, sharp, and professional).

## 3. Fix Broken "Load the case study" & Infinite "WORKING" State
- Debug API Connection & CORS: Ensure the frontend points directly to http://127.0.0.1:8000 (or import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"), remove any perpetual "The solver is starting up. This can take up to a minute." banner once /health responds, and fix why clicking "Load the case study" (both in Hero and Section 04) and solving gets stuck on WORKING.
- Verify Backend Payload: Check that the frontend's request body matches FastAPI's Pydantic schema in backend/app/ and handles errors visibly instead of hanging silently on WORKING.

## 4. Course Table & Difficulty Matrix Redesign
- Single Header Row for Difficulty: Instead of repeating MOST / DIFFICULT / MEDIUM / EASY / EASIEST buttons inside every single course row, place Most Difficult, Difficult, Medium, Easy, and Easiest once in the table header row (with full text, no truncation) and render clean radio/tick boxes under each column per course row.
- Pressing Enter Adds a Row: In the course name input field, pressing Enter must immediately append a new empty course row and move focus to the new course name input.
- Mutually Exclusive Lock vs. Min/Max Logic: When a user enters a value in LOCK (MIN) for a course, automatically disable and clear/lock the MIN (MIN) and MAX (MIN) inputs for that course (with a clear tooltip/indicator) so contradictory constraints cannot be entered.
- Sync Table Constraints with Section B (Rules): Whenever a user enters a MIN, MAX, or LOCK value directly in the course table, automatically display and sync that constraint inside Section B (Rules) below (and vice versa).

## 5. Advanced Settings & Customization
- Custom Difficulty Scale Points: Inside Settings (under Time Available), add editable numeric inputs for the five difficulty multipliers (Most Difficult, Difficult, Medium, Easy, Easiest, defaulting to 1.2, 1.1, 1.0, 0.9, 0.8) so users can customize the scale points as desired.

## 6. Section Hierarchy, Overflow Fixes & Copy Updates
- Section 03 (Method) Layout: Fix the 2-column layout so 03 Method sits cleanly above or beside the text without hugging the left margin awkwardly, and tighten excessive vertical whitespace.
- Section 04 (Case Study) Heading Overflow: Fix the oversized heading CASE STUDY · THIRD-YEAR MATHEMATICS, UNIVERSITY OF CHITTAGONG where CHITTAGONG overlaps the horizontal divider line underneath. Adjust line-height and padding-bottom so the border sits cleanly below the wrapped text.
- Section 05 (About) -> "AUTHOR DETAILS": Rename RESEARCH DETAILS to AUTHOR DETAILS.
- Case Study Report Wording: Replace all references to "paper" or "published paper" (including the footer link Paper and text saying "grew out of a paper") with Case Study Report (e.g., "grew out of a case study report" and footer link Case Study Report).
- Eliminate Unnecessary Blank Spaces: Reduce excess vertical padding/margins between sections and empty areas below paragraphs.