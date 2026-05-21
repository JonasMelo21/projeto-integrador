import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, Loader2 } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { api, Property } from "../services/api";

export function HomePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [areaMin, setAreaMin] = useState(0);
  const [areaMax, setAreaMax] = useState(200);
  const [priceMax, setPriceMax] = useState(10000);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProperties = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProperties(10000);
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

  // Aplicar filtros
  const filteredProperties = displayProperties.filter((property) => {
    // Filtro de área
    if (property.area < areaMin || property.area > areaMax) return false;

    // Filtro de preço
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

          <div className="flex gap-4 items-center flex-wrap">
              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[240px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Área (m²)</span>
                  <span className="text-sm font-medium">{areaMin}m² - {areaMax}m²</span>
                </div>
                <div className="flex gap-3 items-center">
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={areaMin}
                    onChange={(e) => setAreaMin(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={areaMax}
                    onChange={(e) => setAreaMax(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                </div>
              </div>

              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[220px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Preço até</span>
                  <span className="text-sm font-medium">R$ {priceMax.toLocaleString('pt-BR')}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="10000"
                  step="100"
                  value={priceMax}
                  onChange={(e) => setPriceMax(Number(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>
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
            {filteredProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
