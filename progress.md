# Progress

## 0.2.0 review release — 2026-11-23

Prepared the 0.2.0 source package for the public repository [LinfengHarryHu/black-background-figures](https://github.com/LinfengHarryHu/black-background-figures), containing the skill, CLI, verifier, palette guidance, disclosure language, synthetic example and tests. This package does not replace an existing live installation. A source publication is distinct from a tagged release.

Completed:

- Explicit 8-bit PNG input checks and non-overwriting output/audit files.
- Deterministic neutral inversion and exact categorical remapping, with protected regions, unchanged alpha and rejection of observed color collisions.
- Byte-identical keep mode for measurement images.
- Saved-file verification of hashes, per-pixel replay, masks, dimensions and supported color metadata. Neutral inversion is also checked by inverse recovery.
- Twenty local tests passed, including explicit expected pixels, optimized-Python execution, output/mask tampering, protected regions, unsupported inputs and all output-file collisions. See [validation report](tests/validation_report.json).
- The synthetic example was compared visually at full size: labels, minus sign, arrowhead, error bars and category colors remain readable. Its verifier passed all checks. This is an illustrative fixture, not a validation of experimental images or of a slide deck.
- Skill metadata validation passed. No third-party paper figures or personal project paths are included in the public package.

The verifier shares the versioned transformation code; the tests include explicit expected values, but there has been no independent external code review. Reproducible pixel changes do not guarantee equal perceptual visibility or authenticate the supplied original. The supported scope is presentation PNGs, not raw quantitative image processing.

## Next

1. Select a license; no separate open-source license has been granted.
2. Collect feedback on the public source package before deciding whether to publish a tagged release.
3. Collect independent review and examples before expanding supported image formats or transformations. Review each real figure separately; existing slide assets are not retroactively verified by this release.
