import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, Loader2, ChevronLeft, ChevronRight } from "lucide-react";
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
  classificacao_preco?: string;
}

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&h=600&fit=crop";

function mapToProperty(item: BackendImovel): Property {
  return {
    id: String(item.id_imovel),
    title: item.titulo,
    location: `${item.local_bairro || "Brasília"}, Brasília - DF`,
    price: item.preco,
    bedrooms: item.quartos ?? 0,
    bathrooms: 0,
    area: item.area_m2 ?? 0,
    image: item.imagem || FALLBACK_IMAGE,
    mlTag: item.classificacao_preco || "Sem Classificação", // PUXANDO DO ML
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
  
  // Estados para Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 30;
  
  const [areaMin, setAreaMin] = useState(0);
  const [areaMax, setAreaMax] = useState(200);
  const [absoluteMaxArea, setAbsoluteMaxArea] = useState(200);
  
  const [priceMax, setPriceMax] = useState(200000);
  const [absoluteMaxPrice, setAbsoluteMaxPrice] = useState(200000);

  const filters = ["Todos", "Apartamento", "Casa", "Studio", "Barato", "Preço Justo", "Caro"];

  useEffect(() => {
    fetch(`${API_URL}/imoveis?limit=1000`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<BackendImovel[]>;
      })
      .then((data) => {
        setProperties(data.map((d) => mapToProperty(d)));
       
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
  }, []);

  // Resetar a página para 1 sempre que os filtros mudarem
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedFilter, areaMin, areaMax, priceMax]);

  // Aplica todos os filtros primeiro
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
      if (selectedFilter === "Barato" && property.mlTag !== "Barato") return false;
      if (selectedFilter === "Preço Justo" && property.mlTag !== "Preço Justo") return false;
      if (selectedFilter === "Caro" && property.mlTag !== "Caro") return false;
    }
    if (property.area > 0 && (property.area < areaMin || property.area > areaMax)) return false;
    if (property.price > priceMax) return false;
    return true;
  });

  // Fatiar a lista filtrada para mostrar apenas 30 imóveis da página atual
  const totalPages = Math.ceil(filteredProperties.length / ITEMS_PER_PAGE);
  const paginatedProperties = filteredProperties.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

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

        {!loading && !error && filteredProperties.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
              {/* O GRID AGORA RENDERIZA APENAS OS 30 FATIADOS */}
              {paginatedProperties.map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>

            {/* CONTROLES DE PAGINAÇÃO */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-4 mt-10 mb-4">
                <button
                  onClick={() => {
                    setCurrentPage(p => Math.max(1, p - 1));
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  disabled={currentPage === 1}
                  className="p-2 flex items-center gap-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-50 disabled:hover:bg-transparent transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                  <span className="hidden sm:inline">Anterior</span>
                </button>
                
                <span className="text-sm font-medium text-muted-foreground">
                  Página <span className="text-foreground">{currentPage}</span> de {totalPages}
                </span>

                <button
                  onClick={() => {
                    setCurrentPage(p => Math.min(totalPages, p + 1));
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  disabled={currentPage === totalPages}
                  className="p-2 flex items-center gap-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-50 disabled:hover:bg-transparent transition-colors"
                >
                  <span className="hidden sm:inline">Próxima</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}