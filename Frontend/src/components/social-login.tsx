import "./social-login.css";

interface SocialLoginProps {
  text: string;
  bg: string;
  border: string;
  onClickFunc?: (...args: any[]) => any;
}

function SocialLogin({ text, bg, border, onClickFunc }: SocialLoginProps) {
  return (
    <button
      className="social-login"
      style={{ backgroundColor: `${bg}`, border: `${border}` }}
      onClick={onClickFunc}
    >
      {text}
    </button>
  );
}

export default SocialLogin;
