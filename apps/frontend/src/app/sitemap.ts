import type { MetadataRoute } from "next";

const baseUrl = "https://atlas-sentinel.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    "",
    "/command-center",
    "/digital-twin",
    "/incidents",
    "/permits",
    "/compliance",
    "/analytics",
    "/copilot"
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date()
  }));
}
