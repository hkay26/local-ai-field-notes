import {C, Shell} from './design';
export const Opening = () => <Shell chapter="01 / 05">
  <div style={{display: 'flex', gap: 80, alignItems: 'center', height: '100%'}}>
    <div style={{flex: 1}}><div style={{fontSize: 29, color: C.teal, letterSpacing: 4, fontWeight: 700, marginBottom: 36}}>A WORKING PROJECT · AN OPEN RECORD</div><h1 style={{fontSize: 156, letterSpacing: -8, lineHeight: 0.98, margin: 0}}>Local AI.<br/>Open evidence.</h1><p style={{fontSize: 48, lineHeight: 1.25, maxWidth: 930, margin: '40px 0 0'}}>One real experiment on an older PC.<br/>Settings, output and limitations included.</p></div>
    <div style={{width: 420, background: C.ink, color: C.paper, padding: '50px 42px', borderRadius: 6, rotate: '2deg'}}><div style={{fontSize: 26, color: C.mint, letterSpacing: 4}}>FIELD NOTE 001</div><div style={{fontSize: 110, letterSpacing: -5, fontWeight: 700, margin: '36px 0 8px'}}>26.75<span style={{fontSize: 40}}>s</span></div><div style={{fontSize: 35, lineHeight: 1.2}}>End-to-end wall time</div><div style={{height: 2, background: '#5E7378', margin: '38px 0'}}/><div style={{fontSize: 30, lineHeight: 1.5}}>CPU only · 2 threads<br/>Qwen3.5:9b · Q4_K_M<br/>One extraction case</div></div>
  </div>
</Shell>;
