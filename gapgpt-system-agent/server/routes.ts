import express, { Request, Response } from "express";

const router = express.Router();

// Health check route
router.get("/health", (req: Request, res: Response) => {
  res.json({ status: "healthy", service: "GapGPT System Agent API" });
});

// Main API routes
router.get("/", (req: Request, res: Response) => {
  res.json({
    message: "GapGPT System Agent API",
    version: "1.0.0",
    endpoints: ["/health", "/api/agent", "/api/tools"],
  });
});

// Agent endpoints
router.get("/api/agent", (req: Request, res: Response) => {
  res.json({
    status: "active",
    capabilities: ["system_tools", "docker", "file_operations"],
  });
});

// Tools endpoint
router.get("/api/tools", (req: Request, res: Response) => {
  res.json({
    tools: [
      { name: "exec_tools", description: "Execute system commands" },
      { name: "docker_tools", description: "Docker operations" },
      { name: "file_tools", description: "File system operations" },
      { name: "net_tools", description: "Network operations" },
    ],
  });
});

export default router;
