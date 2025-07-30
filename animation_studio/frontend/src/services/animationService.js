import axios from 'axios';
import { API_ENDPOINTS } from '../config/api.js';

class AnimationService {
  constructor() {
    this.api = axios.create({
      baseURL: API_ENDPOINTS.diagnostic.replace('/diagnostic', ''),
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async getDiagnostic() {
    try {
      const response = await this.api.get('/diagnostic');
      return response.data;
    } catch (error) {
      throw new Error(`Erreur diagnostic: ${error.message}`);
    }
  }

  async getThemes() {
    try {
      const response = await this.api.get('/themes');
      return response.data;
    } catch (error) {
      throw new Error(`Erreur récupération thèmes: ${error.message}`);
    }
  }

  async generateAnimation(theme, duration) {
    try {
      // Démarrer la génération avec les vraies IA
      const response = await this.api.post('/generate', {
        theme: theme,
        duration: duration
      });
      return response.data;
    } catch (error) {
      throw new Error(`Erreur génération: ${error.response?.data?.detail || error.message}`);
    }
  }

  async generateAnimationDemo(theme, duration) {
    try {
      // Version démo rapide (pour tests)
      const response = await this.api.post('/generate-quick', null, {
        params: { theme, duration },
        timeout: 600000
      });
      return response.data;
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Timeout: La génération prend trop de temps');
      }
      throw new Error(`Erreur génération: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getAnimationStatus(animationId) {
    try {
      const response = await this.api.get(`/status/${animationId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Erreur statut: ${error.message}`);
    }
  }

  async checkHealth() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

export default new AnimationService(); 