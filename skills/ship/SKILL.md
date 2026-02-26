---
name: ship
description: Deploy and launch a feature or product. Runs a quality gate, pre-launch checklist, and executes deployment. Use when the user is ready to ship.
argument-hint: "optional: project context"
disable-model-invocation: true
---

# Ship: $ARGUMENTS

You are coordinating a launch for the CEO. Time to ship.

## Step 1: Final Quality Gate

Delegate to `@qa` with the project's entry point and test commands. Task: final pre-ship quality gate — run test suites, scan for security vulnerabilities, check for hardcoded secrets or debug artifacts. Report findings using severity format (Critical/Warning/Suggestion/Positive). If any Critical findings, the ship is blocked — STOP and present them to the CEO before proceeding.

## Step 2: Pre-Launch Checklist

Generate a checklist tailored to the project:
- [ ] All tests passing
- [ ] Environment variables configured for production
- [ ] Database migrations ready (if applicable)
- [ ] API keys and secrets secured (not hardcoded)
- [ ] Error monitoring configured (Sentry, etc.)
- [ ] README/docs updated
- [ ] Git changes committed and pushed

Present the checklist to the CEO. Walk through each item — check off what's already done, flag what needs attention. Proceed on approval.

## Step 3: Deploy

Read `.solopreneur/preferences.yaml` for the deployment strategy.

### If deployment is configured (`deployment.configured: true`):

Execute deployment based on the platform:

**Vercel**:
- If Vercel MCP tools are available (`mcp__claude_ai_Vercel__deploy_to_vercel`), use them directly
- Otherwise, run `vercel --prod` via CLI
- After deployment, verify: check build logs for errors, confirm the deployment URL is reachable

**Netlify**:
- Run `netlify deploy --prod` via CLI
- Verify the deployment URL is reachable

**GitHub Pages**:
- Push to the configured branch (typically `gh-pages` or `main`)
- Verify the pages URL is reachable

**Other/Custom**:
- Read `deployment.notes` from preferences for platform-specific instructions
- Delegate to `@engineer` to execute the deployment steps

**For all platforms:**
- Report the live URL to the CEO (ephemeral — shown in conversation, not saved to a file)
- If deployment fails, show the error and offer to troubleshoot with the `@engineer`
- If `deployment.rollback` is not yet in preferences, generate platform-specific rollback instructions and save them

### If deployment is deferred (`deployment.configured: false` or `deployment.platform: none`):

Ask the CEO:
> Your code is ready to go, but we haven't set up deployment yet.
> Want to set that up now? I can help you pick a platform and get it running.

If yes, follow the same deployment setup flow as `/build` Step 1.75 (ask platform, configure, deploy). Save to preferences.

If no, skip deployment — just ensure git changes are committed and pushed.

### If no deployment config exists at all:

Same as the deferred case above. This handles legacy projects or situations where `/build` wasn't used.

## Step 4: Post-Deploy Verification

If deployment was executed:
1. Wait briefly for the deployment to propagate
2. Check the live URL is responding (delegate to `@qa` if browser tools are available)
3. Report status to the CEO (all ephemeral — shown in conversation, not saved to files):
   - Deployment URL
   - Build status (success/failure)
   - Any warnings from the build logs
   - Rollback instructions (also saved in preferences.yaml for future reference)

## Step 5: Next Steps

End with the next step prompt:
```
-> Next: Announce the launch:
   /solopreneur:release-notes "customers"
   /solopreneur:release-notes "social media"
```
