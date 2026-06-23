import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, Loader2 } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { Property } from "../type";

const API_URL = "http://localhost:8000/api";

interface BackendImovel {
  id_imovel: number;
  titulo: string;
  preco: number;
  area_m2: number;
  imagem: string;
  quartos: number | null;
  imobiliaria_nome: string | null;
  local_bairro: string | null;
}

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&h=600&fit=crop";

function mapToProperty(item: BackendImovel, avgPrice: number): Property {
  return {
    id: String(item.id_imovel),
    title: item.titulo,
    location: `${item.local_bairro || "Brasília"}, Brasília - DF`,
    price: item.preco,
    bedrooms: item.quartos ?? 0,
    bathrooms: 0,
    area: item.area_m2 ?? 0,
    image: item.imagem || FALLBACK_IMAGE,
    mlTag: item.preco <= avgPrice ? "Preço Justo" : "Oportunidade",
    images: [item.imagem || FALLBACK_IMAGE],
    description: "",
    priceComparison: 0,
    amenities: [],
  };
}

export function HomePage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("Todos");
  
  const [areaMin, setAreaMin] = useState(0);
  const [areaMax, setAreaMax] = useState(200);
  const [absoluteMaxArea, setAbsoluteMaxArea] = useState(200);
  
  const [priceMax, setPriceMax] = useState(200000);
  const [absoluteMaxPrice, setAbsoluteMaxPrice] = useState(200000);

  const filters = ["Todos", "Apartamento", "Casa", "Studio", "Preço Justo", "Oportunidade"];

  useEffect(() => {
    fetch(`${API_URL}/imoveis?limit=1000`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<BackendImovel[]>;
      })
      .then((data) => {
        const avg = data.reduce((sum, d) => sum + d.preco, 0) / (data.length || 1);
        setProperties(data.map((d) => mapToProperty(d, avg)));
       
        // Dinamismo de Preço
        const maxPrice = Math.max(...data.map((d) => d.preco), 10000);
        setAbsoluteMaxPrice(maxPrice); 
        setPriceMax(maxPrice);         

        // Dinamismo de Área
        const maxArea = Math.max(...data.map((d) => d.area_m2 || 0), 200);
        setAbsoluteMaxArea(maxArea);
        setAreaMax(maxArea);

        setLoading(false);
      })
      .catch(() => {
        setError("Não foi possível conectar ao backend.");
        setLoading(false);
      });
  }, []); // <--- ESTE É O FECHAMENTO QUE ESTAVA FALTANDO!

  const filteredProperties = properties.filter((property) => {
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      if (
        !property.title.toLowerCase().includes(term) &&
        !property.location.toLowerCase().includes(term)
      )
        return false;
    }
    if (selectedFilter !== "Todos") {
      const title = property.title.toLowerCase();
      if (selectedFilter === "Apartamento" && !title.includes("apartamento")) return false;
      if (selectedFilter === "Casa" && !title.includes("casa")) return false;
      if (
        selectedFilter === "Studio" &&
        !title.includes("studio") &&
        !title.includes("kitnet") &&
        !title.includes("loft")
      )
        return false;
      if (selectedFilter === "Preço Justo" && property.mlTag !== "Preço Justo") return false;
      if (selectedFilter === "Oportunidade" && property.mlTag !== "Oportunidade") return false;
    }
    if (property.area > 0 && (property.area < areaMin || property.area > areaMax)) return false;
    if (property.price > priceMax) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-6 md:py-8">
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por localização, bairro ou cidade..."
                className="w-full pl-12 pr-4 py-3 md:py-4 border border-border rounded-xl bg-card focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
              />
            </div>
            <button className="p-3 md:p-4 border border-border rounded-xl bg-card hover:bg-secondary transition-colors shadow-sm">
              <SlidersHorizontal className="w-5 h-5 text-foreground" />
            </button>
          </div>

          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {filters.map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSelectedFilter(filter)}
                  className={`px-4 py-2 rounded-full whitespace-nowrap transition-all ${
                    selectedFilter === filter
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <div className="flex gap-4 items-center flex-wrap">
              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[240px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Área (m²)</span>
                  <span className="text-sm font-medium">
                    {areaMin}m² - {areaMax}m²
                  </span>
                </div>
                <div className="flex gap-3 items-center">
                  <input
                    type="range"
                    min="0"
                    max={absoluteMaxArea}
                    value={areaMin}
                    onChange={(e) => setAreaMin(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                  <input
                    type="range"
                    min="0"
                    max={absoluteMaxArea}
                    value={areaMax}
                    onChange={(e) => setAreaMax(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                </div>
              </div>

              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[220px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Preço até</span>
                  <span className="text-sm font-medium">
                    R$ {priceMax.toLocaleString("pt-BR")}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max={absoluteMaxPrice}
                  step="500"
                  value={priceMax}
                  onChange={(e) => setPriceMax(Number(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20 gap-3 text-muted-foreground">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Carregando imóveis...</span>
          </div>
        )}

        {error && (
          <div className="text-center py-20 text-destructive">
            <p>{error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Certifique-se de que o backend está rodando em localhost:8000
            </p>
          </div>
        )}

        {!loading && !error && filteredProperties.length === 0 && (
          <div className="text-center py-20 text-muted-foreground">
            Nenhum imóvel encontrado com os filtros aplicados.
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            {filteredProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}