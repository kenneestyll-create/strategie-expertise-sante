import { useMemo } from 'react';

const PARTICLES = [
  // Bottom zone — high density
  { w: 3, h: 3, top: '88%', left: '5%', opacity: 0.5, anim: 'goldShimmer1', dur: '4s', delay: '0s' },
  { w: 2, h: 2, top: '92%', left: '12%', opacity: 0.35, anim: 'goldShimmer2', dur: '3.5s', delay: '0.5s' },
  { w: 4, h: 4, top: '85%', left: '20%', opacity: 0.45, anim: 'goldShimmer3', dur: '5s', delay: '1s' },
  { w: 2, h: 2, top: '90%', left: '28%', opacity: 0.3, anim: 'goldShimmer1', dur: '4.2s', delay: '0.3s' },
  { w: 3, h: 3, top: '95%', left: '35%', opacity: 0.4, anim: 'goldShimmer2', dur: '3.8s', delay: '1.5s' },
  { w: 5, h: 5, top: '87%', left: '45%', opacity: 0.55, anim: 'goldShimmer1', dur: '5.5s', delay: '0.8s' },
  { w: 2, h: 2, top: '93%', left: '52%', opacity: 0.25, anim: 'goldShimmer3', dur: '4s', delay: '2s' },
  { w: 3, h: 3, top: '89%', left: '60%', opacity: 0.4, anim: 'goldShimmer2', dur: '3.2s', delay: '0.6s' },
  { w: 4, h: 4, top: '91%', left: '68%', opacity: 0.5, anim: 'goldShimmer1', dur: '4.8s', delay: '1.2s' },
  { w: 2, h: 2, top: '86%', left: '75%', opacity: 0.35, anim: 'goldShimmer3', dur: '3.5s', delay: '0.2s' },
  { w: 3, h: 3, top: '94%', left: '82%', opacity: 0.45, anim: 'goldShimmer2', dur: '5s', delay: '1.8s' },
  { w: 6, h: 6, top: '88%', left: '90%', opacity: 0.5, anim: 'goldShimmer1', dur: '4.5s', delay: '0.4s' },
  { w: 2, h: 2, top: '96%', left: '95%', opacity: 0.3, anim: 'goldShimmer3', dur: '3.8s', delay: '1.1s' },
  // Mid-bottom zone — moderate density
  { w: 2, h: 2, top: '72%', left: '8%', opacity: 0.2, anim: 'goldShimmer2', dur: '5s', delay: '0.7s' },
  { w: 3, h: 3, top: '78%', left: '18%', opacity: 0.3, anim: 'goldShimmer1', dur: '4.5s', delay: '1.3s' },
  { w: 2, h: 2, top: '75%', left: '32%', opacity: 0.25, anim: 'goldShimmer3', dur: '3.8s', delay: '0.9s' },
  { w: 4, h: 4, top: '80%', left: '55%', opacity: 0.35, anim: 'goldShimmer2', dur: '5.2s', delay: '0.1s' },
  { w: 2, h: 2, top: '73%', left: '70%', opacity: 0.2, anim: 'goldShimmer1', dur: '4s', delay: '2.2s' },
  { w: 3, h: 3, top: '82%', left: '85%', opacity: 0.3, anim: 'goldShimmer3', dur: '3.5s', delay: '1.6s' },
  { w: 2, h: 2, top: '76%', left: '92%', opacity: 0.25, anim: 'goldShimmer2', dur: '4.8s', delay: '0.5s' },
  // Mid zone — sparse
  { w: 2, h: 2, top: '55%', left: '3%', opacity: 0.15, anim: 'goldShimmer3', dur: '5.5s', delay: '1s' },
  { w: 2, h: 2, top: '50%', left: '25%', opacity: 0.1, anim: 'goldShimmer1', dur: '4.2s', delay: '2.5s' },
  { w: 3, h: 3, top: '60%', left: '48%', opacity: 0.2, anim: 'goldShimmer2', dur: '5s', delay: '0.3s' },
  { w: 2, h: 2, top: '52%', left: '78%', opacity: 0.15, anim: 'goldShimmer3', dur: '3.8s', delay: '1.8s' },
  { w: 2, h: 2, top: '65%', left: '93%', opacity: 0.2, anim: 'goldShimmer1', dur: '4.5s', delay: '0.7s' },
  // Upper zone — very sparse
  { w: 2, h: 2, top: '15%', left: '10%', opacity: 0.08, anim: 'goldShimmer2', dur: '5.5s', delay: '2s' },
  { w: 2, h: 2, top: '25%', left: '40%', opacity: 0.1, anim: 'goldShimmer3', dur: '4.8s', delay: '1.4s' },
  { w: 2, h: 2, top: '20%', left: '65%', opacity: 0.08, anim: 'goldShimmer1', dur: '5s', delay: '0.9s' },
  { w: 2, h: 2, top: '30%', left: '88%', opacity: 0.12, anim: 'goldShimmer2', dur: '4.2s', delay: '2.3s' },
  { w: 2, h: 2, top: '10%', left: '50%', opacity: 0.06, anim: 'goldShimmer3', dur: '5.8s', delay: '1.7s' },
  // Edges — subtle accent
  { w: 3, h: 3, top: '40%', left: '1%', opacity: 0.15, anim: 'goldShimmer1', dur: '4s', delay: '0.8s' },
  { w: 3, h: 3, top: '45%', left: '97%', opacity: 0.15, anim: 'goldShimmer2', dur: '4.5s', delay: '1.5s' },
  { w: 4, h: 4, top: '83%', left: '40%', opacity: 0.4, anim: 'goldDrift', dur: '6s', delay: '0s' },
  { w: 3, h: 3, top: '90%', left: '15%', opacity: 0.35, anim: 'goldDrift', dur: '7s', delay: '1s' },
  { w: 3, h: 3, top: '85%', left: '72%', opacity: 0.3, anim: 'goldDrift', dur: '5.5s', delay: '2s' },
];

export const GoldDustOverlay = () => {
  const particles = useMemo(() => PARTICLES, []);

  return (
    <div className="gold-particles" aria-hidden="true">
      {particles.map((p, i) => (
        <div
          key={i}
          className="gold-particle"
          style={{
            width: p.w,
            height: p.h,
            top: p.top,
            left: p.left,
            opacity: p.opacity,
            animation: `${p.anim} ${p.dur} ease-in-out ${p.delay} infinite`,
          }}
        />
      ))}
    </div>
  );
};
