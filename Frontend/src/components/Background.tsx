import { ReactNode, useState, useEffect } from "react";
import "../App.css";
import Cloud from "./cloud";

interface ForegroundProps {
  logo: Boolean;
  footer: 1 | 2;
  children?: ReactNode;
}

// Cloud sizes in viewport width percentage
const cloudSizes = [0, 10, 14]; // 0, ~15vw, ~20vw

// Cloud positions in viewport width percentage
const cloudPos = {
  posX: [0, 18, 0, 16, 35, 20, 26], // percentage of viewport width
  posY: [0, 8, 26, 25, 0, 40, 20], // percentage of viewport height
  type: [2, 1, 2, 1, 1, 1, 1] as const,
  flipped: [false, false, false, true, true, false, false],
};

export default function Background({
  logo,
  footer,
  children,
}: ForegroundProps) {
  return (
    <div>
      {cloudPos.posX.map((_, i) => (
        <>
          {/* Clouds on Left half  */}
          <Cloud
            key={2 * i}
            posX={cloudPos.posX[i]}
            posY={cloudPos.posY[i]}
            type={cloudPos.type[i]}
            flipped={cloudPos.flipped[i]}
            usePercentage={true}
          />

          {/* Clouds on right half  */}
          <Cloud
            key={2 * i + 1}
            posX={100 - cloudPos.posX[i] - cloudSizes[cloudPos.type[i]]}
            posY={cloudPos.posY[i]}
            type={cloudPos.type[i]}
            flipped={!cloudPos.flipped[i]}
            usePercentage={true}
          />
        </>
      ))}
      {logo ? (
        <div className="w-full flex justify-center relative z-10 -mt-40">
          <img
            src="assets/Logo.png"
            className="w-[28vw] min-w-[280px] py-8"
            alt="Tic-Tac-Tactics Logo"
          />
        </div>
      ) : null}
      <div className="relative z-10 w-full">{children}</div>

      <img
        src={`assets/Bottom${footer}.png`}
        className="w-[100vw] min-w-[280px] fixed bottom-0 left-0"
        alt="Footer"
      />
    </div>
  );
}
