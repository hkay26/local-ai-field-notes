# Verified free community text inference

AI Horde offers shared volunteer text generation through an anonymous REST API.
The official [anonymous-use instructions](https://github.com/Haidra-Org/AI-Horde#anonymous-usage)
and [integration documentation](https://github.com/Haidra-Org/AI-Horde/blob/main/README_integration.md)
describe the service. No personal account, payment card or local GPU was used
for the two recorded requests. Anonymous requests have the lowest queue
priority, and availability changes. This is not a dedicated GPU allocation.

## What was actually observed

The [two-attempt record](../examples/2026-10-18-horde-gemma4.json) preserves an
initial failure and a successful response on October 18, 2026, submitted through
PowerShell's HTTP client. The initial generic instruction wrapper with a
64-token cap returned explanatory text. A separate request used the official
[Gemma 4 no-thinking format](https://ai.google.dev/gemma/docs/capabilities/thinking)
and a 128-token cap, returning:

```json
{"city":"Houston","day":"Tuesday","attendees":12}
```

The exact request bodies, job receipts and completed responses are retained.
The successful response passed a JSON parser with the expected city/day and
integer attendee count. Both jobs reported complete, with no fault.

These are changed configurations, not repeated identical trials. The model
label `google/gemma-4-31b` comes from the service; weights, quantization and host
hardware were not independently verified. No speed or quality ranking follows
from this one narrow check. Only fictional data was submitted.

## Current client limitation

A later standalone Python-client experiment received HTTP 403. A read-only
catalog check through that client also returned HTTP 403, error code 1010.
That client is not published as ready, and no identity change or further API
submission was attempted. The earlier completed responses establish what
worked at that time, not guaranteed access for every client or future session.

For current supported interfaces and help, use the service's official
[documentation and community links](https://aihorde.net/).
