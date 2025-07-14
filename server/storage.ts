import { 
  type Location, 
  type Delivery, 
  type RouteOptimizationResult,
  type InsertDelivery 
} from "@shared/schema";
import fs from 'fs';
import path from 'path';

export interface IStorage {
  getLocations(): Promise<Location[]>;
  getDeliveries(): Promise<Delivery[]>;
  createDelivery(delivery: InsertDelivery): Promise<Delivery>;
  updateDelivery(id: string, delivery: Partial<Delivery>): Promise<Delivery>;
  deleteDelivery(id: string): Promise<void>;
  getCityMap(): Promise<any>;
}

export class MemStorage implements IStorage {
  private locations: Map<string, Location>;
  private deliveries: Map<string, Delivery>;
  private cityMap: any;

  constructor() {
    this.locations = new Map();
    this.deliveries = new Map();
    this.cityMap = null;
    this.loadInitialData();
  }

  private async loadInitialData() {
    try {
      // Load city map
      const cityMapPath = path.join(process.cwd(), 'server/data/city_map.json');
      const cityMapData = fs.readFileSync(cityMapPath, 'utf-8');
      this.cityMap = JSON.parse(cityMapData);

      // Load locations from city map
      if (this.cityMap && this.cityMap.locations) {
        this.cityMap.locations.forEach((location: Location) => {
          this.locations.set(location.id, location);
        });
      }

      // Load deliveries
      const deliveriesPath = path.join(process.cwd(), 'server/data/deliveries.json');
      const deliveriesData = fs.readFileSync(deliveriesPath, 'utf-8');
      const deliveries = JSON.parse(deliveriesData);
      
      if (deliveries && deliveries.deliveries) {
        deliveries.deliveries.forEach((delivery: Delivery) => {
          this.deliveries.set(delivery.id, delivery);
        });
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  }

  async getLocations(): Promise<Location[]> {
    return Array.from(this.locations.values());
  }

  async getDeliveries(): Promise<Delivery[]> {
    return Array.from(this.deliveries.values());
  }

  async createDelivery(insertDelivery: InsertDelivery): Promise<Delivery> {
    const id = `D${Date.now()}`;
    const delivery: Delivery = { ...insertDelivery, id };
    this.deliveries.set(id, delivery);
    return delivery;
  }

  async updateDelivery(id: string, updateData: Partial<Delivery>): Promise<Delivery> {
    const delivery = this.deliveries.get(id);
    if (!delivery) {
      throw new Error('Delivery not found');
    }
    const updatedDelivery = { ...delivery, ...updateData };
    this.deliveries.set(id, updatedDelivery);
    return updatedDelivery;
  }

  async deleteDelivery(id: string): Promise<void> {
    if (!this.deliveries.has(id)) {
      throw new Error('Delivery not found');
    }
    this.deliveries.delete(id);
  }

  async getCityMap(): Promise<any> {
    return this.cityMap;
  }
}

export const storage = new MemStorage();
