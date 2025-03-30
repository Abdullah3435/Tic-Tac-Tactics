import React from "react";
import "./circular-button.css";

// Import icons from HeroIcons
import { IconType } from "react-icons";
import * as HIcons from "react-icons/hi";

interface CircularButtonProps {
  icon: keyof typeof HIcons;
  onClick?: () => void;
  className?: string;
}

const CircularButton: React.FC<CircularButtonProps> = ({ icon, onClick }) => {
  // Dynamically get the icon component from HeroIcons
  const IconComponent = HIcons[icon] as IconType;

  return (
    <button className="circular-button" onClick={onClick} type="button">
      <IconComponent />
    </button>
  );
};

export default CircularButton;
