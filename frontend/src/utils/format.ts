import type { TimeUnit } from "../types";

export function formatTimeMinutes(minutes: number): string {
  const m = Math.round(minutes);
  return `${m} min`;
}

export function formatTimeHours(minutes: number): string {
  const totalM = Math.round(minutes);
  if (totalM < 60) {
    return `${totalM} min`;
  }
  const h = Math.floor(totalM / 60);
  const rem = totalM % 60;
  return rem > 0 ? `${h} h ${rem} m` : `${h} h`;
}

export function formatTimeWithAlt(minutes: number, activeUnit: TimeUnit): { primary: string; secondary: string } {
  if (activeUnit === "min") {
    const primary = formatTimeMinutes(minutes);
    const secondary = formatTimeHours(minutes);
    return { primary, secondary: secondary !== primary ? secondary : "" };
  } else {
    const primary = formatTimeHours(minutes);
    const secondary = formatTimeMinutes(minutes);
    return { primary, secondary: secondary !== primary ? secondary : "" };
  }
}
