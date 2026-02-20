---
name: ship
description: Deploy and launch a feature or product. Generates a deployment checklist and coordinates launch preparation. Use when the user is ready to ship.
disable-model-invocation: true
---

# Ship: $ARGUMENTS

You are coordinating a launch for the CEO. Time to ship.

## Process

1. **Final Quality Gate**: Delegate to the `@qa` subagent for a final review:
   - Run existing test suites if available (`npm test`, `pytest`, etc.)
   - Check for any critical or warning-level issues
   - If QA finds critical issues, STOP and present them to the CEO before proceeding

2. **Pre-Launch Checklist**: Generate a checklist tailored to the project:
   - [ ] All tests passing
   - [ ] Environment variables configured for production
   - [ ] Database migrations ready (if applicable)
   - [ ] API keys and secrets secured (not hardcoded)
   - [ ] Error monitoring configured (Sentry, etc.)
   - [ ] Rollback plan documented
   - [ ] README/docs updated
   - [ ] Git changes committed and pushed

3. **Release Notes**: Generate release notes from recent git commits:
   - What's new (features)
   - What's fixed (bugs)
   - What's changed (breaking changes, if any)

4. Present the checklist to the CEO. Proceed step by step on approval.

5. End with the next step prompt:
   ```
   -> Next: Announce the launch with:
      /solopreneur:release-notes "customers"
      /solopreneur:release-notes "internal team"
      /solopreneur:release-notes "social media"
   ```
