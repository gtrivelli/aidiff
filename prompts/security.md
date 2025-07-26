# Security Review Prompt

# SECURITY REVIEW OUTPUT FORMAT INSTRUCTION
# Add this at the end of the prompt to enforce strict markdown output from the LLM

# Respond ONLY in the following markdown format for each issue found:
#
# ---
# **Issue:** <short description>
# **File:** <filename>
# **Line Number:** <line number(s)>
# **Code:** <the flagged line(s)>
# **Severity:** <Critical/High/Medium/Low>
# **Confidence:** <0-100%>
# **Suggestion:** <actionable fix>
# ---
#
# Do not include any prose, summary, or extra recommendations outside this format.
