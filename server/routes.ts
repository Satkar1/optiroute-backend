import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { spawn } from "child_process";
import path from "path";
import { 
  deliverySchema, 
  routeConfigSchema, 
  insertDeliverySchema 
} from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Get all locations
  app.get("/api/locations", async (req, res) => {
    try {
      const locations = await storage.getLocations();
      res.json(locations);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch locations" });
    }
  });

  // Get all deliveries
  app.get("/api/deliveries", async (req, res) => {
    try {
      const deliveries = await storage.getDeliveries();
      res.json(deliveries);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch deliveries" });
    }
  });

  // Create delivery
  app.post("/api/deliveries", async (req, res) => {
    try {
      const validatedData = insertDeliverySchema.parse(req.body);
      const delivery = await storage.createDelivery(validatedData);
      res.status(201).json(delivery);
    } catch (error) {
      res.status(400).json({ error: "Invalid delivery data" });
    }
  });

  // Update delivery
  app.put("/api/deliveries/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const delivery = await storage.updateDelivery(id, req.body);
      res.json(delivery);
    } catch (error) {
      res.status(404).json({ error: "Delivery not found" });
    }
  });

  // Delete delivery
  app.delete("/api/deliveries/:id", async (req, res) => {
    try {
      const { id } = req.params;
      await storage.deleteDelivery(id);
      res.status(204).send();
    } catch (error) {
      res.status(404).json({ error: "Delivery not found" });
    }
  });

  // Get city map
  app.get("/api/city-map", async (req, res) => {
    try {
      const cityMap = await storage.getCityMap();
      res.json(cityMap);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch city map" });
    }
  });

  // Optimize route
  app.post("/api/optimize-route", async (req, res) => {
    try {
      const config = routeConfigSchema.parse(req.body);
      const deliveries = await storage.getDeliveries();
      const cityMap = await storage.getCityMap();

      // Call Python Flask service for route optimization
      const result = await callFlaskService('optimize-route', {
        config,
        deliveries,
        cityMap
      });

      res.json(result);
    } catch (error) {
      console.error('Route optimization error:', error);
      res.status(500).json({ error: "Failed to optimize route" });
    }
  });

  // Plan capacity using knapsack algorithm
  app.post("/api/plan-capacity", async (req, res) => {
    try {
      const { deliveries, capacity } = req.body;
      
      const result = await callFlaskService('plan-capacity', {
        deliveries,
        capacity
      });

      res.json(result);
    } catch (error) {
      console.error('Capacity planning error:', error);
      res.status(500).json({ error: "Failed to plan capacity" });
    }
  });

  // Save delivery plan
  app.post("/api/save-plan", async (req, res) => {
    try {
      const deliveries = await storage.getDeliveries();
      
      const result = await callFlaskService('save-plan', {
        deliveries
      });

      res.json(result);
    } catch (error) {
      console.error('Save plan error:', error);
      res.status(500).json({ error: "Failed to save plan" });
    }
  });

  // Get route history
  app.get("/api/route-history", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 10;
      
      const result = await callFlaskService('get-history', {
        limit
      });

      res.json(result);
    } catch (error) {
      console.error('Route history error:', error);
      res.status(500).json({ error: "Failed to get route history" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

// Helper function to call Flask service
async function callFlaskService(endpoint: string, data: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(process.cwd(), 'server/flask_app.py'),
      endpoint,
      JSON.stringify(data)
    ]);

    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${error}`));
      } else {
        try {
          const parsed = JSON.parse(result);
          resolve(parsed);
        } catch (parseError) {
          reject(new Error(`Failed to parse Python response: ${parseError}`));
        }
      }
    });
  });
}
