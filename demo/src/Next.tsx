import {C, Eyebrow, Shell, Title} from './design';
export const Next = () => <Shell chapter="05 / 05">
  <Eyebrow>THE NEXT EXPERIMENT</Eyebrow><Title>More hardware.<br/>The same open record.</Title>
  <div style={{display: 'flex', gap: 64, marginTop: 52}}><div style={{flex: 1, fontSize: 42, lineHeight: 1.42}}>Planned: GPU adapters, repeated runs,<br/>and clear reproduction notes.<br/><span style={{color: C.teal, fontWeight: 700}}>Support requests are pending.</span></div><div style={{width: 630, padding: '30px 35px', background: C.mint, fontSize: 34, lineHeight: 1.4}}>Independent beginner creator.<br/>No established audience yet.<br/>No hardware sponsor approved.</div></div>
  <div style={{borderTop: `2px solid ${C.line}`, marginTop: 44, paddingTop: 29}}><div style={{fontSize: 41, fontWeight: 700, letterSpacing: -1}}>github.com/hkay26/local-ai-field-notes</div><div style={{fontSize: 29, color: C.muted, marginTop: 17}}>MIT-licensed code · Raw measured record · Project brief</div></div>
</Shell>;
