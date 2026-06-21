import { MapPin, Search } from "lucide-react";
import { mockProperties } from "../data/mockData";
import { useState } from "react";
import { useNavigate } from "react-router";

export function MapPage() {
  const [selectedProperty, setSelectedProperty] = useState<string | null>(null);
  const navigate = useNavigate();

  return (
    <div className="h-full bg-background relative">
      <div className="absolute top-4 left-4 right-4 z-10">
        <div className="max-w-md mx-auto">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar por localização..."
              className="w-full pl-12 pr-4 py-3 border border-border rounded-xl bg-card focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-lg"
            />
          </div>
        </div>
      </div>

      <div className="w-full h-full bg-muted relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <MapPin className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p>Mapa Interativo</p>
            <p className="text-sm">(Demonstração)</p>
          </div>
        </div>

        {mockProperties.slice(0, 5).map((property, index) => (
          <div
            key={property.id}
            className="absolute"
            style={{
              top: `${20 + index * 15}%`,
              left: `${15 + index * 12}%`,
            }}
          >
            <button
              onClick={() => setSelectedProperty(property.id)}
              className="relative group"
            >
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-lg ${
                  selectedProperty === property.id
                    ? "bg-primary scale-125"
                    : "bg-card hover:scale-110"
                }`}
              >
                <MapPin
                  className={`w-6 h-6 ${
                    selectedProperty === property.id
                      ? "text-primary-foreground"
                      : "text-primary"
                  }`}
                />
              </div>
              <div className="absolute -top-1 -right-1 w-5 h-5 bg-warning text-warning-foreground rounded-full flex items-center justify-center text-xs shadow-md">
                {property.bedrooms}
              </div>
            </button>
          </div>
        ))}
      </div>

      {selectedProperty && (
        <div className="absolute bottom-4 left-4 right-4 z-10">
          <div className="max-w-md mx-auto bg-card border border-border rounded-2xl shadow-2xl overflow-hidden">
            {(() => {
              const property = mockProperties.find(
                (p) => p.id === selectedProperty
              );
              if (!property) return null;

              return (
                <div
                  onClick={() => navigate(`/property/${property.id}`)}
                  className="cursor-pointer"
                >
                  <div className="relative h-40">
                    <img
                      src={property.image}
                      alt={property.title}
                      className="w-full h-full object-cover"
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProperty(null);
                      }}
                      className="absolute top-3 right-3 w-8 h-8 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-all shadow-md"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="p-4">
                    <h3 className="mb-2 line-clamp-1">{property.title}</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      {property.location}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-primary">
                        R$ {property.price.toLocaleString()}/mês
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs ${
                          property.mlTag === "Preço Justo"
                            ? "bg-success text-success-foreground"
                            : "bg-warning text-warning-foreground"
                        }`}
                      >
                        {property.mlTag}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
