import {C, Eyebrow, Shell, Title} from './design';
export const Result = () => <Shell chapter="03 / 05">
  <Eyebrow>THE MEASURED RESULT</Eyebrow><Title>Three numbers.<br/>Three different meanings.</Title>
  <div style={{display: 'flex', gap: 28, marginTop: 52}}>
    <div style={{flex: 1, borderTop: `8px solid ${C.teal}`, paddingTop: 24}}><div style={{fontSize: 104, fontWeight: 700, letterSpacing: -5}}>26.75<span style={{fontSize: 43}}> s</span></div><div style={{fontSize: 39, fontWeight: 700}}>Client wall time</div><p style={{fontSize: 29, color: C.muted, lineHeight: 1.35}}>Request start through completion,<br/>including setup and loading.</p></div>
    <div style={{flex: 1, borderTop: `8px solid ${C.ink}`, paddingTop: 24}}><div style={{fontSize: 104, fontWeight: 700, letterSpacing: -5}}>19.29<span style={{fontSize: 43}}> s</span></div><div style={{fontSize: 39, fontWeight: 700}}>First answer content</div><p style={{fontSize: 29, color: C.muted, lineHeight: 1.35}}>First non-empty answer received.<br/>Not tokenizer-level first-token time.</p></div>
    <div style={{flex: 1, borderTop: `8px solid ${C.ink}`, paddingTop: 24}}><div style={{fontSize: 104, fontWeight: 700, letterSpacing: -5}}>3.49<span style={{fontSize: 35}}> tok/s</span></div><div style={{fontSize: 39, fontWeight: 700}}>Runtime generation</div><p style={{fontSize: 29, color: C.muted, lineHeight: 1.35}}>26 reported tokens / 7.46 seconds.<br/>Different from end-to-end speed.</p></div>
  </div>
  <div style={{fontSize: 30, color: C.teal, fontWeight: 700, marginTop: 15}}>One CPU-only run. No GPU ranking or statistical claim.</div>
</Shell>;
