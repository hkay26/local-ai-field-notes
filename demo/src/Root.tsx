import {Composition, Folder, Series, useVideoConfig} from 'remotion';
import {Opening} from './Opening';
import {Method} from './Method';
import {Result} from './Result';
import {Evidence} from './Evidence';
import {Next} from './Next';

const ReviewerDemo = () => {
  const {fps} = useVideoConfig();
  return <Series>
    <Series.Sequence name="Opening" durationInFrames={8 * fps} premountFor={fps}><Opening/></Series.Sequence>
    <Series.Sequence name="Method" durationInFrames={12 * fps} premountFor={fps}><Method/></Series.Sequence>
    <Series.Sequence name="Measured result" durationInFrames={15 * fps} premountFor={fps}><Result/></Series.Sequence>
    <Series.Sequence name="Evidence" durationInFrames={13 * fps} premountFor={fps}><Evidence/></Series.Sequence>
    <Series.Sequence name="Next experiment" durationInFrames={12 * fps} premountFor={fps}><Next/></Series.Sequence>
  </Series>;
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="ReviewerDemo" component={ReviewerDemo} durationInFrames={1800} fps={30} width={1920} height={1080}/>
      <Folder name="Scenes">
        <Composition id="Opening" component={Opening} durationInFrames={240} fps={30} width={1920} height={1080}/>
        <Composition id="Method" component={Method} durationInFrames={360} fps={30} width={1920} height={1080}/>
        <Composition id="MeasuredResult" component={Result} durationInFrames={450} fps={30} width={1920} height={1080}/>
        <Composition id="Evidence" component={Evidence} durationInFrames={390} fps={30} width={1920} height={1080}/>
        <Composition id="NextExperiment" component={Next} durationInFrames={360} fps={30} width={1920} height={1080}/>
      </Folder>
    </>
  );
};
