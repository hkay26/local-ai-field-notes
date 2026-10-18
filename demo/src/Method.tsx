import {C, Eyebrow, Shell, Title} from './design';
export const Method = () => <Shell chapter="02 / 05">
  <Eyebrow>THE TASK</Eyebrow><Title>Turn a fictional event<br/>into strict JSON.</Title>
  <div style={{display: 'flex', gap: 45, marginTop: 48}}><div style={{width: '56%', padding: '32px 40px', background: C.white, borderLeft: `8px solid ${C.teal}`}}><div style={{fontSize: 25, color: C.teal, fontWeight: 700, letterSpacing: 3}}>FICTIONAL INPUT</div><div style={{fontSize: 54, lineHeight: 1.26, marginTop: 24}}>A Houston workshop.<br/>Tuesday. 12 attendees.</div></div><div style={{flex: 1, fontSize: 35, lineHeight: 1.6, paddingTop: 10}}>i7-8700K · 32 GB RAM<br/>Ollama 0.32.9 · CPU only<br/>Context 512 · Output cap 64<br/>Temperature 0 · Seed 42</div></div>
  <p style={{fontSize: 31, color: C.muted, marginTop: 34}}>Fictional test data. No private records. Exact prompt and model digest are public.</p>
</Shell>;
