// Service d'authentification JWT avec refresh tokens
const API_BASE_URL = 'http://localhost:8007';

class JWTAuthService {
    constructor() {
        this.accessToken = localStorage.getItem('jwt_access_token');
        this.refreshToken = localStorage.getItem('jwt_refresh_token');
        this.isRefreshing = false;
        this.failedQueue = [];
    }

    // Gestion de la file d'attente pour les requêtes échouées
    processQueue(error, token = null) {
        this.failedQueue.forEach(prom => {
            if (error) {
                prom.reject(error);
            } else {
                prom.resolve(token);
            }
        });
        this.failedQueue = [];
    }

    // Connexion
    async login(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur de connexion');
            }

            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token);
            
            // Stocker les informations utilisateur
            localStorage.setItem('userEmail', email);
            
            return { success: true, data };
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw error;
        }
    }

    // Inscription
    async register(email, password, firstName, lastName) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email, 
                    password, 
                    first_name: firstName, 
                    last_name: lastName 
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur d\'inscription');
            }

            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token);
            
            // Stocker les informations utilisateur
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userName', `${firstName} ${lastName}`);
            localStorage.setItem('userFirstName', firstName);
            localStorage.setItem('userLastName', lastName);
            
            return { success: true, data };
        } catch (error) {
            console.error('Erreur d\'inscription:', error);
            throw error;
        }
    }

    // Rafraîchir le token
    async refreshToken() {
        if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
                this.failedQueue.push({ resolve, reject });
            });
        }

        this.isRefreshing = true;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: this.refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Erreur de rafraîchissement du token');
            }

            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token);
            this.processQueue(null, data.access_token);
            
            return data.access_token;
        } catch (error) {
            this.processQueue(error, null);
            this.logout();
            throw error;
        } finally {
            this.isRefreshing = false;
        }
    }

    // Déconnexion
    async logout() {
        try {
            if (this.refreshToken) {
                await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh_token: this.refreshToken }),
                });
            }
        } catch (error) {
            console.error('Erreur lors de la déconnexion:', error);
        } finally {
            this.clearTokens();
            localStorage.clear();
            window.location.href = '/';
        }
    }

    // Vérifier si l'utilisateur est connecté
    isAuthenticated() {
        return !!(this.accessToken && this.refreshToken);
    }

    // Obtenir le token d'accès
    getAccessToken() {
        return this.accessToken;
    }

    // Définir les tokens
    setTokens(accessToken, refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('jwt_access_token', accessToken);
        localStorage.setItem('jwt_refresh_token', refreshToken);
    }

    // Effacer les tokens
    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('jwt_access_token');
        localStorage.removeItem('jwt_refresh_token');
    }

    // Requête authentifiée avec gestion automatique du refresh
    async authenticatedRequest(url, options = {}) {
        if (!this.accessToken) {
            throw new Error('Utilisateur non authentifié');
        }

        // Ajouter le token d'accès aux headers
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.accessToken}`,
            ...options.headers,
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            if (response.status === 401) {
                // Token expiré, essayer de le rafraîchir
                try {
                    const newToken = await this.refreshToken();
                    headers.Authorization = `Bearer ${newToken}`;
                    
                    // Réessayer la requête avec le nouveau token
                    const retryResponse = await fetch(url, {
                        ...options,
                        headers,
                    });
                    
                    if (!retryResponse.ok) {
                        throw new Error(`Erreur HTTP: ${retryResponse.status}`);
                    }
                    
                    return await retryResponse.json();
                } catch (refreshError) {
                    // Refresh échoué, déconnecter l'utilisateur
                    this.logout();
                    throw new Error('Session expirée, veuillez vous reconnecter');
                }
            }

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erreur de requête authentifiée:', error);
            throw error;
        }
    }

    // Récupérer le profil utilisateur
    async getProfile() {
        return await this.authenticatedRequest(`${API_BASE_URL}/auth/profile`);
    }

    // Mettre à jour le profil utilisateur
    async updateProfile(profileData) {
        return await this.authenticatedRequest(`${API_BASE_URL}/auth/profile`, {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
    }

    // Vérifier la validité du token
    async verifyToken() {
        try {
            return await this.authenticatedRequest(`${API_BASE_URL}/auth/verify`);
        } catch (error) {
            return { valid: false };
        }
    }

    // Réinitialisation de mot de passe
    async resetPassword(email) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur de réinitialisation');
            }

            return await response.json();
        } catch (error) {
            console.error('Erreur de réinitialisation:', error);
            throw error;
        }
    }
}

// Instance globale
const jwtAuthService = new JWTAuthService();

export default jwtAuthService; 