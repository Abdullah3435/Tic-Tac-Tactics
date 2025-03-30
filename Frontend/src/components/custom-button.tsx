import React from "react";
import "./custom-button.css";

interface ButtonProps {
  text: string;
  onClickFunc?: () => void;
  variant?: "primary-button" | "secondary-button";
  size?: "large" | "small";
}

function CustomButton({
  text,
  onClickFunc,
  variant = "primary-button",
  size = "large",
}: ButtonProps) {
  return (
    <button className={`${variant} ${size}`} onClick={onClickFunc}>
      {text}
    </button>
  );
}

export default CustomButton;
