---
name: black-background-figures
description: Adapt scientific figures for black-background slides using unchanged source data or deterministic pixel color transforms, with hashes, masks and replay verification. Preserve molecular colors and provenance; retain measurement images and unsuitable shaded figures on their original background.
---

# Black-background scientific figures

Choose the route from the source's provenance. A dark theme never justifies reconstructing scientific evidence.

1. **Existing plotting/rendering code and data or coordinates:** make a presentation variant from the same observations, analysis and coordinates. Change style and camera only as appropriate. Preserve units, uncertainty, atom/chain identity and legend meaning. Keep the original code/data and a source manifest. This route is not verified by the pixel helper.
2. **Published image only:** preserve the original and use the deterministic helper below for suitable line art. Do not trace, redraw, sharpen, denoise, erase, invent bonds, resample observations or use generative image editing. An independently documented crop is a separate operation.
3. **Gels, fluorescence, microscopy, continuous color scales or shaded figures with lost detail:** retain original pixels on a light panel. Measurement brightness is evidence. Use `--kind measurement --mode keep` for a byte-identical copy.

Read [palette guidance](references/palette.md) when choosing colors and [verification/disclosure boundaries](references/verification.md) before reporting an image as verified. Keep category labels and legends. Do not promise that all details remain equally visible after color changes.

## Deterministic pixel workflow

Install the Python dependencies in `requirements.txt`. Use **8-bit PNG** presentation copies, retaining the original publication or scientific raw file separately. The helper refuses high-bit-depth, palette, animated and rotated-EXIF inputs rather than silently changing their meaning. A grayscale ICC-profile input needs a separately documented RGB export.

```bash
python scripts/pixel_theme.py original.png dark.png --kind line-art
python scripts/verify_theme.py dark.json --source original.png
```

Default `--chroma-tolerance 0` inverts only exactly achromatic RGB pixels. All RGB channels at selected coordinates become `255 - channel`; alpha is unchanged. A nonzero tolerance up to 32 includes near-neutral colored pixels, so **do not claim all colored pixels are unchanged** when using it. Inspect antialiased edges before increasing tolerance.

`--protect x,y,width,height` excludes a rectangle, in input pixel coordinates. `--color-map map.json` supplies exact `#RRGGBB` pairs applied to the original pixel colors, overriding inversion at those pixels. Apply the same category mapping to its legend; protect measurements. Maps that merge distinct observed source colors are refused. Arbitrary remapping is not advertised as having the same inverse guarantee as neutral inversion.

The helper produces output PNG, selection-mask PNG, before/after comparison and a JSON manifest with parameters, tool/dependency versions and hashes. Existing outputs or sidecars are never overwritten. Source paths in the manifest are basenames; use `--source` and `--output` overrides if moving the files.

Run verification against the saved output, then inspect original/adapted views and the intended slide. Check faint lines, minus signs, error bars, atom colors, arrows, legends and shading. Record accepted/rejected status separately with reasons. A valid replay proves only that the documented transformation produced those pixels relative to the supplied source. It cannot establish the source's authenticity or perceptual equivalence.

Keep source, output, manifest, mask and verification result together with the slide provenance. If the dark version loses clarity, use the original light panel. Project-specific language, typography and author preferences belong in project instructions rather than this reusable skill.
