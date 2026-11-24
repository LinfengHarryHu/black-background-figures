# Verification boundaries and disclosure

## Guarantees that are actually checked

| Property | Evidence |
| --- | --- |
| Same image grid | Source and output dimensions; no resize/crop/warp operation in the pixel transform |
| Same pixel coordinates | Per-coordinate replay of the declared rule |
| Same alpha | Exact array equality |
| Same unselected/protected pixels | Exact RGBA equality, not approximate similarity |
| Declared selection only | Saved mask, mask hash and exact selection replay |
| Saved output matches computation | Decode the actual PNG and compare every RGBA value |
| Neutral inversion is reversible | Invert selected RGB values again using the saved mask; compare original decoded pixels |
| Source identity | Retained source-file hash and decoded-pixel hash |

Neutral inversion preserves distinct intensities **inside an inverted region** through a one-to-one mapping. It does not preserve the absolute intensity values, global contrast relationships across selected/protected boundaries, or viewers' interpretation. A nonzero chroma tolerance includes near-neutral colors. Do not describe that as preserving every colored pixel.

Exact categorical maps override inversion for matching original colors. Distinct observed source colors may not merge into one output RGB value. This conservative check does not guarantee that two different output colors are visually distinguishable. The neutral-inversion inverse test is intentionally not claimed for arbitrary maps.

## What the audit cannot prove

- That a supplied source is the authentic published image. Retain DOI, figure/panel identifier, original PDF and crop/export record separately.
- That there were no edits before the supplied PNG, or after the verified output was placed in a slide.
- That a font, faint edge, shaded atom or error bar remains equally easy to see.
- That an image classification is correct: `--kind measurement` is a user declaration, not an image-content detector.
- That restyled plots use unchanged numerical data, or molecular re-renders use unchanged coordinates. Those routes need their own manifests and checks.
- That metadata is cryptographically signed, or that a person cannot replace source, output and records together.
- That this tool is suitable for raw quantitative image analysis or journal evidence-image processing.

## Review procedure

1. Retain the publication/raw source; document any independent export and crop.
2. Choose the narrowest suitable transformation and save parameters.
3. Run the read-only verifier against the actual saved files.
4. Compare original and adapted views at full size and at projected slide size. Check atom/strand colors and their legend together, thin lines, minus signs, arrowheads, error bars, labels and shading.
5. Record accepted/rejected status and reason. Keep the original background if adaptation is misleading or less clear.
6. Retain the accepted asset's hash in the slide-source manifest. Recheck after further image edits; uniform display scaling is separate from the pixel transform.

## Useful wording

“Deterministic pixel-color transformation” or “source-preserving color adaptation” describes the operation. “AI-generated figure,” “pixel-level generation,” “guaranteed no detail changes,” and “forensically certified” would misdescribe this tool or overstate its guarantees.

For an oral answer:

> AI helped me write the code, but it did not regenerate the figure. The script applies an explicit color rule at the existing pixel coordinates. We retain the original image and a mask showing every selected pixel, and the verifier reproduces the output exactly. I also compare the figures visually because recoloring can still affect contrast.

For a coordinate-derived molecular animation:

> This view was rendered from the cited deposited coordinates with a changed camera and presentation colors. It is a visualization of those coordinates, not an experimental movie or a simulated trajectory.
