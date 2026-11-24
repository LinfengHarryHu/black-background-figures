# Palette and figure decisions

Use black `#000000`, main text `#F6F7FA`, and secondary text `#BCC5D1`. On black, prefer cyan `#56B4E9`, amber `#FFCB3B`, rose `#EF4797`, mint `#48C97D`, and lavender `#B9A6FF`. Keep no more than three simultaneous accent meanings in an ordinary panel. Avoid saturated dark blue, dark red, and green/red-only comparisons.

For VIPR, preserve guide RNA = rose, target DNA = amber, nontarget DNA = green. In original paper crops, preserve the original chain colors and include their legend. Gray is protein context; a highlighted residue may use cyan and an explicit label. Never reuse a chain color as an unrelated verdict of success or failure on the same figure.

For ZnO coordinate renders, use O = coral `#FF7878`, N = light blue `#64A9FF`, S = yellow `#F3D35B`, C = pale gray `#B9C2CC`, H = white, Zn = blue-gray `#9FB1C1`. A selected atom may use a labeled outline rather than changing its elemental color. Site-specific colors from an accepted figure can be kept if its labels and legend are retained.

For new data plots, pair cyan circles/solid curves with amber squares/dashed curves. Additional series may use rose triangles and white diamonds. Preserve overlaps and replicate counts. A color adjustment must not change a y-axis scale, omit data, or convert a categorical value into a quantitative color scale.

Compute relative sRGB luminance. Use at least 4.5:1 text/background contrast as a conservative slide-design check, despite large text having a lower WCAG threshold. Thin lines and projected figures need additional visual review. Ratios do not establish legibility in a meeting room or distinguish two adjacent hues.

Sources: [W3C contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [W3C use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html). These are web-accessibility principles used here as design checks, not a claim of certified slide accessibility.

## When to keep a light panel

- Quantitative brightness, gray-level measurement, or continuous color scale.
- Black atom outlines or dark colored bonds disappear after inversion.
- Shaded molecular surfaces develop halos or lose depth cues.
- Original labels are too small; enlarge a crop with its context instead of reconstructing its data.
- No reliable way to preserve the meaning of every category and legend.

Pure black-and-white conversion is inappropriate when colors identify atoms, strands, mutants, or experimental conditions. Neutral inversion preserves colored pixels; it does not guarantee those colors are bright enough on black. Inspect and decide panel by panel.
