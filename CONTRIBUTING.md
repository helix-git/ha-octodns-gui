# Contributing

## Conventional Commits

Dieses Repository verwendet [Conventional Commits](https://www.conventionalcommits.org/) für automatische Versionierung.

### Commit-Typen

| Typ | Beschreibung | Version-Bump |
|-----|--------------|--------------|
| `fix:` | Bugfix | Patch (0.0.x) |
| `feat:` | Neues Feature | Minor (0.x.0) |
| `feat!:` oder `BREAKING CHANGE:` | Breaking Change | Major (x.0.0) |
| `docs:` | Dokumentation | Kein Release |
| `chore:` | Wartung | Kein Release |
| `refactor:` | Code-Refactoring | Kein Release |
| `test:` | Tests | Kein Release |

### Beispiele

```bash
# Bugfix
git commit -m "fix: Korrigiere Zone-Parsing bei leeren Records"

# Neues Feature
git commit -m "feat: Füge DNS Provider Auswahl hinzu"

# Breaking Change
git commit -m "feat!: Ändere Zone-Datei Format"
```

## Release-Workflow

```
1. Code ändern
2. Commit mit Conventional Commit Message
3. Push nach `main` Branch
4. Release-Please erstellt automatisch einen PR
5. PR reviewen und mergen
6. Automatisch:
   - Release wird erstellt
   - Docker Images werden gebaut (aarch64, amd64)
   - config.yaml Version wird aktualisiert
   - haos-apps Repository wird synchronisiert
```

## Pull Requests

1. Branch von `main` erstellen:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/mein-feature
   ```

2. Änderungen committen:
   ```bash
   git add .
   git commit -m "feat: Beschreibung des Features"
   ```

3. Push und PR erstellen:
   ```bash
   git push origin feature/mein-feature
   gh pr create --base main
   ```

## Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/helix-git/ha-octodns-gui.git
cd ha-octodns-gui

# Docker Build testen
docker build \
  --build-arg BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21" \
  -t test-octodns-gui .

# Container starten
docker run -it --rm \
  -e SUPERVISOR_TOKEN="test" \
  -e ZONE_FILE_PATH="/tmp/zones" \
  -p 8100:8100 \
  test-octodns-gui
```
