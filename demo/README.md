# Field Note 001 — editable reviewer preview

A 60-second, 1920×1080, 30 fps silent Remotion composition explaining the
repository's real CPU-only Qwen3.5:9b extraction run. It uses original text and
layout, system fonts, and no external media or paid services.

## Preview

With a supported Node.js version, from this folder:

```sh
npm ci
npm run dev -- --no-open
```

Open the localhost URL printed by Studio, then choose **ReviewerDemo**.
Five separately editable scenes are grouped under **Scenes**. The main timeline
uses 8, 12, 15, 13 and 12 seconds respectively. The first half-second of each
scene fades in; seek past it to inspect a still layout.

```sh
npm run lint
```

The dependencies are locked to Remotion 4.0.536 and React 19.2.3. Remotion's own
license governs the renderer; the authored source code is covered by the
repository MIT license. Check the current Remotion terms for your own use.

## Evidence and scope

The [storyboard](../docs/storyboard.md) contains visually checked scene stills.
The source figures come from the [raw measured record](../examples/2026-10-18-cpu-extraction.json).
The preview identifies the run as CPU only, with two threads, and separates
client wall time, first answer-content latency and runtime generation speed.
The ten passing tests verify the runner; they do not establish general model quality.

Current status is an editable preview and stills. Narration, additional measured
runs, hardware evaluation and creator-channel publication are future work.
