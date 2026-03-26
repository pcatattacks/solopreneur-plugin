# Installing Solopreneur for Codex

Enable Solopreneur in Codex using Codex's native skill discovery.

## Prerequisites

- OpenAI Codex CLI
- Git

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/pcatattacks/solopreneur-plugin.git ~/.codex/solopreneur-plugin
   ```

2. **Create the skills symlink:**

   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/solopreneur-plugin/.agents/skills/solopreneur ~/.agents/skills/solopreneur
   ```

   **Windows (PowerShell):**

   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\solopreneur" "$env:USERPROFILE\.codex\solopreneur-plugin\.agents\skills\solopreneur"
   ```

3. **Restart Codex** to pick up the new skills.

## Verify

```bash
ls -la ~/.agents/skills/solopreneur
```

You should see the Solopreneur skill directories such as `using-solopreneur/`, `solopreneur-build/`, and `solopreneur-review/`.

## Updating

```bash
cd ~/.codex/solopreneur-plugin && git pull
```

## Uninstalling

```bash
rm ~/.agents/skills/solopreneur
```

Optionally remove the clone:

```bash
rm -rf ~/.codex/solopreneur-plugin
```
