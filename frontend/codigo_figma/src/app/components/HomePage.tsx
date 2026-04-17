import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, Loader2 } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { api, Property } from "../services/api";

export function HomePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("Todos");
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const filters = [
    "Todos",
    "Apartamento",
    "Casa",
    "Studio",
    "Preço Justo",
    "Oportunidade",
  ];

  useEffect(() => {
    const loadProperties = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProperties(50);
        setProperties(data);
      } catch (err) {
        setError("Falha ao carregar imóveis");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadProperties();
  }, []);

  // Converter dados da API para formato esperado pelo PropertyCard
  const displayProperties = properties.map((p) => ({
    id: p.id_imovel.toString(),
    title: p.titulo,
    location: `${p.local_bairro}, ${p.local_cidade} - ${p.local_uf}`,
    price: p.preco,
    bedrooms: p.quartos,
    bathrooms: p.banheiros,
    area: p.area_m2,
    image: p.imagem || "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop",
    mlTag: (p.preco < 3000 ? "Preço Justo" : "Oportunidade") as "Preço Justo" | "Oportunidade",
    images: [p.imagem || "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop"],
    description: p.descricao || "",
    priceComparison: 0,
    amenities: [],
  }));

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
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <p className="text-destructive">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            {displayProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
