const API_BASE = "http://localhost:8000/api";

export interface Property {
  id_imovel: number;
  id_hex: string;
  titulo: string;
  url: string;
  preco: number;
  area_m2: number;
  quartos: number;
  banheiros: number;
  vagas: number;
  imagem: string;
  descricao: string;
  data_extracao: string;
  imobiliaria_nome: string;
  local_bairro: string;
  local_cidade: string;
  local_uf: string;
}

export interface PropertyDetail extends Property {
  images: string[];
}

export const api = {
  async getProperties(limit: number = 10000, skip: number = 0): Promise<Property[]> {
    try {
      const response = await fetch(
        `${API_BASE}/imoveis?skip=${skip}&limit=${limit}`,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok) throw new Error("Falha ao buscar imóveis");
      return await response.json();
    } catch (error) {
      console.error("Erro ao buscar imóveis:", error);
      return [];
    }
  },

  async getPropertyById(id: number): Promise<PropertyDetail | null> {
    try {
      const response = await fetch(`${API_BASE}/imoveis/${id}`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) throw new Error("Imóvel não encontrado");
      const property = await response.json();
      return {
        ...property,
        images: property.imagem ? [property.imagem] : [],
      };
    } catch (error) {
      console.error("Erro ao buscar imóvel:", error);
      return null;
    }
  },

  async getPropertyByHex(id_hex: string): Promise<PropertyDetail | null> {
    try {
      const response = await fetch(`${API_BASE}/imoveis/by-hex/${id_hex}`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) throw new Error("Imóvel não encontrado");
      const property = await response.json();
      return {
        ...property,
        images: property.imagem ? [property.imagem] : [],
      };
    } catch (error) {
      console.error("Erro ao buscar imóvel:", error);
      return null;
    }
  },

  async getStats(): Promise<{
    total_imoveis: number;
    preco_medio: number;
    area_media_m2: number;
  }> {
    try {
      const response = await fetch(`${API_BASE}/imoveis/stats`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) throw new Error("Falha ao buscar estatísticas");
      return await response.json();
    } catch (error) {
      console.error("Erro ao buscar estatísticas:", error);
      return {
        total_imoveis: 0,
        preco_medio: 0,
        area_media_m2: 0,
      };
    }
  },
};
