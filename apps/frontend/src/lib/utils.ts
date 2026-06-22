export function riskTone(score: number) {
  if (score >= 80) return "red";
  if (score >= 60) return "orange";
  if (score >= 40) return "yellow";
  return "green";
}
