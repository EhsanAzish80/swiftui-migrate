# Roadmap

Future plans for swiftui-migrate.

## v1.0 (Current)

**Status:** Stable

**Features:**
- Regex-based pattern detection
- 5 deprecated API rules (iOS 14-16)
- 5 fragile pattern rules
- JSON output for CI
- Inline annotation mode (opt-in)
- Deterministic output
- GitHub Actions integration

**Philosophy:** Boring and reliable. No auto-refactoring.

## v1.1 (Planned)

**Focus:** More rules

- Additional iOS 17 deprecations
- More fragile patterns from community
- Custom rule definitions (YAML/JSON)
- Rule disable comments in code

**Timeline:** TBD

## v2.0 (Future)

**Focus:** Swift AST parsing

Replace regex with proper Swift syntax parsing:

- More accurate detection
- Fewer false positives
- Context-aware analysis
- Better handling of complex code

**Why not now?**
- Regex works well enough for v1
- AST parsing is complex (requires Swift compiler/SourceKit)
- Adds dependencies and maintenance burden
- Would slow down the tool

**Timeline:** When regex becomes insufficient

## v3.0 (Maybe)

**Focus:** Auto-refactoring (opt-in only)

**Possible features:**
- `--fix` flag to automatically rewrite code
- Preview mode (show diff before applying)
- Safety checks (backup, dry-run)
- Per-rule enable/disable

**Requirements:**
- Must be opt-in
- Must support preview/dry-run
- Must create backups
- Must be conservative (no breaking changes)

**Why not now?**
- Auto-refactoring is risky
- Requires AST manipulation
- High complexity, low ROI for v1
- Community needs to validate v1/v2 first

**Timeline:** If there's strong demand and AST support exists

## Not Planned

**Things we won't do:**

- ❌ Xcode extension - Out of scope
- ❌ VSCode extension - Out of scope
- ❌ GUI application - CLI tool only
- ❌ AI-powered suggestions - No AI, no magic
- ❌ Cloud service - Local tool only
- ❌ Automatic PR creation - User control only
- ❌ Build system integration - CI is enough

## Community Requests

**Want a feature?**

1. Check [GitHub Issues](https://github.com/EhsanAzish80/swiftui-migrate/issues)
2. Open a new issue with:
   - Clear use case
   - Example code
   - Why regex isn't enough
3. Be patient - this is a side project

**Contributing rules:**

Most valuable contribution: new detection rules!

Submit via PR with:
- Rule ID and name
- Pattern to detect
- iOS version
- Migration suggestion
- Example code (before/after)
- Test case

See existing rules in `src/swiftui_migrate/rules.py` for format.

## Design Principles

All future versions will follow:

1. **Boring is good** - No magic, no AI, no hype
2. **Opt-in features** - Never break existing workflows
3. **Deterministic** - Same input = same output
4. **Fast** - No compilation, no heavy processing
5. **Transparent** - Show what will change before changing
6. **Conservative** - Don't break working code
7. **Local** - No cloud services, no telemetry
8. **Open** - Community-driven rules and priorities

## Version Support

**Python:** 3.10+ (will track Python release schedule)

**Swift:** Pattern-based, works with all Swift versions

**iOS versions:** Rules cover iOS 14-17 currently, will add new versions as Apple releases them

**Breaking changes:** Semantic versioning (major.minor.patch)
- v1.x → v2.x: Breaking CLI changes
- v1.1 → v1.2: New features, backward compatible
- v1.1.1 → v1.1.2: Bug fixes only

## Current Limitations

Things we know about:

- Regex-based (no AST) - false positives/negatives possible
- English-only messages
- No custom rule files (yet)
- No IDE integration
- No real-time scanning
- No incremental mode (scans all files every time)

These may be addressed in future versions if there's demand.

## Timeline Philosophy

**No fixed dates.**

This is a side project maintained by volunteers. Features ship when they're ready and thoroughly tested.

If you need a feature urgently, consider:
- Contributing a PR
- Hiring commercial support (if available)
- Using an alternative tool

## Stay Updated

Watch the [GitHub repository](https://github.com/EhsanAzish80/swiftui-migrate) for:
- New releases
- Feature announcements
- Community discussions
- Breaking changes
