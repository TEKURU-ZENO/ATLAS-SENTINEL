export function riskStreamUrl() {
  return `${API_BASE_URL.replace("http", "ws")}/ws/risk`;
}

import { API_BASE_URL } from "./api";
