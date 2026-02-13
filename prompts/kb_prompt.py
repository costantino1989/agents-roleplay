KB_PROMPT = """# PROMPT FOR EXTRACTING GENERATIONAL BEHAVIORAL PATTERNS FROM SURVEY DATA

Carefully analyze the following survey questions and response options from the SimBench dataset to extract **concrete behavioral patterns, values, and generational norms**.

## CRITICAL INSTRUCTION: FOCUS ON BEHAVIOR, NOT SURVEY DESIGN

**DO NOT analyze the survey itself** (e.g., "the question implies...", "the inclusion of this option suggests...").

**DO extract behavioral rules** from what the questions reveal about expected or normalized behaviors for each generation.

### Example of WRONG approach:
❌ "The inclusion of 'civil union' in the question signals that researchers expect Millennials to use alternative legal frameworks"

### Example of CORRECT approach:
✅ "Millennials in Finland and France are presented with 'civil union' as a normalized relationship option alongside marriage, indicating that for this generation, legal partnerships exist on a spectrum rather than a binary. This reflects values of institutional flexibility and relationship autonomy over traditional marriage mandates."

---

## WHAT TO EXTRACT

For each generation represented in the examples, identify and extract:

1. **Observed behavioral patterns** – Life choices, attitudes toward institutions (marriage, family, work), existential priorities that are **reflected or implied by the question topics**

2. **Core values** – What drives decisions: stability, freedom, tradition, innovation, individualism, collectivism. Infer these from the **types of behaviors being measured**

3. **Socio-cultural context** – Formative historical events, economic conditions, social norms that explain **why these particular behaviors are being measured** for this generation

4. **Attitude toward change and tradition** – What does the question's framing reveal about this generation's relationship with traditional vs. emerging norms?

5. **Inferred work priorities** – If questions touch on labor (unions, training, work-life balance), what do the response options tell us about generational workplace values?

6. **Relational expectations** – How does this generation relate to authority, peers, institutions based on **what behaviors are considered relevant to measure**?

7. **Cross-cultural variations** – Note when the same question appears across countries but cultural context might shift its meaning

8. **Intergenerational differences** – Note when question topics or framings differ between Millennials and Gen Z samples

9. **Normalized behaviors** – What actions are treated as "normal enough to measure" for this cohort? (e.g., cohabitation, union membership, continuous learning)

10. **Emerging vs. declining norms** – Which institutions/behaviors are still relevant? Which are fading?

---

## OUTPUT FORMAT

Return the analysis as a **list of JSON objects**, where each object contains a behavioral observation and its metadata.

### Required JSON structure:

{{ "doc": "Complete, self-contained behavioral observation", "metadata": ["label1", "label2", "label3"] }}

### Rules for the "doc" field:

- Must describe a **concrete behavioral pattern or generational norm**
- Must be self-contained and understandable without external context
- Always include reference to the generation (Millennials or Gen Z)
- Always include the year and country/countries where relevant
- Link observations to the specific question topics when possible
- **Avoid meta-commentary on survey design** — focus on what behaviors are being normalized/measured
- Maintain a neutral and analytical tone
- Frame observations as "Generation X demonstrates/shows/exhibits/normalizes..." NOT "The survey suggests..."

### Rules for the "metadata" field:

List of labels for filtering and categorization.

**Mandatory labels:**

- Generation: MUST always include `"millennials"` or `"genz"`
- At least one behavioral category (e.g., `"relationship_norms"`, `"labor_attitudes"`, `"religious_identity"`)

**Recommended label types:**
- Behavioral domain: `"cohabitation_patterns"`, `"union_engagement"`, `"continuous_learning"`, `"digital_behavior"`
- Values: `"autonomy"`, `"pragmatism"`, `"institutional_skepticism"`, `"flexibility"`
- Geographic: Country names or regions (`"Finland"`, `"Nordic_countries"`, `"Southern_Europe"`)
- Temporal: `"2016_context"`, `"post_2008_crisis"`, `"digital_native_era"`
- Comparative: `"intergenerational_shift"`, `"cross_cultural_variation"`

---

## TEXTS TO ANALYZE

{documents}

---

## EXISTING DOCUMENTS (do not duplicate)

{older_doc}

If this section contains documents, make sure NOT to create duplicate or very similar observations. Analyze the new
examples and extract only patterns, values, and insights NOT already captured in existing documents.

---

## EXPECTED OUTPUT

Provide a valid JSON list of objects, where each element follows the structure {{"doc": "...", "metadata": [...]}}.

**Important:**

- Return ONLY the JSON array
- NO markdown code fences (no ```json or ```)
- NO additional text before or after the JSON
- Ensure the JSON is valid and parsable
- EACH object MUST have `"millennials"` or `"genz"` in the metadata
- Create consistent and useful metadata labels to facilitate later filtering
- Avoid creating duplicates compared to already existing documents
- Focus on BEHAVIORAL PATTERNS, not survey methodology"""
