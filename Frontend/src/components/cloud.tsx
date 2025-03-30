import "../App.css";

interface CloudProps {
  posX: number;
  posY: number;
  type: 1 | 2;
  flipped?: boolean;
  usePercentage?: boolean;
}

export default function Cloud({
  posX,
  posY,
  type,
  flipped = false,
  usePercentage = false,
}: CloudProps) {
  // Define cloud widths based on type
  const cloudWidth = type === 1 ? "10vw" : "14vw";

  return (
    <img
      src={`assets/cloud${type}.png`}
      alt="Cloud"
      className="absolute z-0 opacity-100"
      style={{
        transform: flipped ? "scaleX(-1)" : "scaleX(1)",
        left: usePercentage ? `${posX}vw` : `${posX}px`,
        top: usePercentage ? `${posY}vh` : `${posY}px`,
        width: usePercentage ? cloudWidth : "auto",
      }}
    />
  );
}
