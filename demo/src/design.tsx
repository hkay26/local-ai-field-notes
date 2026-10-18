import type {ReactNode} from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

export const C = {ink: '#111F29', paper: '#F2F1E9', muted: '#66747A', teal: '#007C69', mint: '#C3F0D9', line: '#CBD4CD', white: '#FCFCF5'};
export const Shell = ({children, chapter, dark = false}: {children: ReactNode; chapter: string; dark?: boolean}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  return <AbsoluteFill style={{background: dark ? C.ink : C.paper, color: dark ? C.paper : C.ink, fontFamily: 'Arial, sans-serif', padding: '76px 104px', overflow: 'hidden'}}>
    <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 29, fontWeight: 700, letterSpacing: 3, paddingBottom: 26, borderBottom: `2px solid ${dark ? '#53616A' : C.line}`}}>
      <div><span style={{color: dark ? C.mint : C.teal}}>◧</span> LOCAL AI FIELD NOTES</div><div>{chapter}</div>
    </div>
    <div style={{flex: 1, position: 'relative', opacity: interpolate(frame, [0, 0.55 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)}), translate: interpolate(frame, [0, 0.55 * fps], ['0px 28px', '0px 0px'], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{children}</div>
    <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 27, color: dark ? '#B9C6C9' : C.muted, paddingTop: 25, borderTop: `2px solid ${dark ? '#53616A' : C.line}`}}><span>HAMZA MOHAMMAD KHAN · HOUSTON</span><span>RECORDED 18 OCT 2026</span></div>
    <div style={{position: 'absolute', bottom: 0, left: 0, height: 7, background: dark ? C.mint : C.teal, width: `${interpolate(frame, [0, durationInFrames - 1], [0, 100])}%`}} />
  </AbsoluteFill>;
};
export const Eyebrow = ({children}: {children: ReactNode}) => <div style={{fontSize: 28, fontWeight: 700, letterSpacing: 4, color: C.teal, marginTop: 53, marginBottom: 23}}>{children}</div>;
export const Title = ({children, size = 116}: {children: ReactNode; size?: number}) => <h1 style={{fontSize: size, fontWeight: 700, letterSpacing: -6, lineHeight: 1.02, margin: 0}}>{children}</h1>;
