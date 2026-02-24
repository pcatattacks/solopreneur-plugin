# Example: SaaS Startup Founder

## Profile
A solo founder building a B2B SaaS product. Handles everything from code to customer support.

## Employees (Agents)
1. **Product Manager** - Prioritizes features, writes specs, manages roadmap
2. **Full-Stack Engineer** - Implements features, fixes bugs, manages infrastructure
3. **Growth Marketer** - SEO, content marketing, landing page optimization, analytics
4. **Customer Success** - Writes support responses, creates help docs, analyzes churn

## SOPs (Skills)
1. `/saas:feature-idea` - Evaluate and prioritize a feature request
2. `/saas:sprint-plan` - Plan a 1-2 week sprint from the backlog
3. `/saas:build` - Generate implementation plan for a feature
4. `/saas:launch` - Coordinate a feature launch (deploy + announce + docs)
5. `/saas:support` - Draft a customer support response
6. `/saas:churn-analysis` - Analyze why users are leaving and propose fixes
7. `/saas:metrics` - Generate a weekly metrics report
8. `/saas:kickoff` - Collaborative team meeting using agent teams

## Team Meetings (Agent Teams)
Invoke with `/saas:kickoff [team-name] [topic]`:
1. **Sprint Planning**: Product Manager + Engineer + Growth Marketer
2. **Launch Team**: Engineer + Growth Marketer + Customer Success
3. **Retention Review**: Customer Success + Product Manager + Growth Marketer

## Tools (MCP Servers)
- GitHub (code management)
- Stripe (billing, revenue data)
- PostHog or Mixpanel (analytics)
- Intercom or Zendesk (support tickets)

## Lifecycle
`/feature-idea` → `/sprint-plan` → `/build` → `/launch` → `/metrics` (use `/kickoff` any time for team discussions)
