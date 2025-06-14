
import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { Button } from "./ui/button";

const THEME_KEY = "theme-preference";

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    const val = localStorage.getItem(THEME_KEY);
    if (val) return val === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem(THEME_KEY, dark ? "dark" : "light");
  }, [dark]);

  return (
    <Button variant="ghost" size="icon" aria-label={dark ? "Light mode" : "Dark mode"} onClick={() => setDark(d => !d)}>
      {dark ? <Sun size={20} /> : <Moon size={20} />}
    </Button>
  );
}
