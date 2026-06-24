import { Heart, Bed, Bath, MapPin } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";
import { Property } from "../type";

interface PropertyCardProps {
  property: Property;
}

export function PropertyCard({ property }: PropertyCardProps) {
  const [isFavorite, setIsFavorite] = useState(false);
  const navigate = useNavigate();

  // Lógica de cores baseada no ML
  const getBadgeStyle = (tag: string) => {
    switch (tag) {
      case "Barato":
        return "bg-green-100 text-green-800 border border-green-200"; // Oportunidade
      case "Preço Justo":
        return "bg-blue-100 text-blue-800 border border-blue-200"; // Padrão
      case "Caro":
        return "bg-red-100 text-red-800 border border-red-200"; // Acima do mercado
      default:
        return "bg-gray-100 text-gray-800 border border-gray-200"; // Fallback
    }
  };

  return (
    <div
      onClick={() => navigate(`/property/${property.id}`)}
      className="bg-card rounded-xl overflow-hidden border border-border hover:shadow-xl transition-all cursor-pointer group flex flex-col"
    >
      <div className="relative h-48 overflow-hidden">
        <img
          src={property.image}
          alt={property.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
        />
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsFavorite(!isFavorite);
          }}
          className="absolute top-3 right-3 p-2 bg-white/90 rounded-full hover:bg-white transition-all shadow-md z-10"
        >
          <Heart
            className={`w-5 h-5 ${
              isFavorite ? "fill-red-500 text-red-500" : "text-gray-600"
            }`}
          />
        </button>
        <div className="absolute top-3 left-3 z-10">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold shadow-sm backdrop-blur-sm bg-opacity-90 ${getBadgeStyle(property.mlTag)}`}
          >
            {property.mlTag || "Não Avaliado"}
          </span>
        </div>
      </div>

      <div className="p-4 flex flex-col flex-1 justify-between">
        <div>
          <h3 className="line-clamp-2 mb-2 text-base font-semibold leading-tight">{property.title}</h3>
          <div className="flex items-center gap-1 text-muted-foreground mb-3 text-sm">
            <MapPin className="w-4 h-4 shrink-0" />
            <span className="line-clamp-1">{property.location}</span>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-4 mb-4 text-muted-foreground text-sm">
            <div className="flex items-center gap-1">
              <Bed className="w-4 h-4" />
              <span>{property.bedrooms}</span>
            </div>
            <div className="flex items-center gap-1">
              <Bath className="w-4 h-4" />
              <span>{property.bathrooms}</span>
            </div>
            <div className="text-xs bg-secondary px-2 py-1 rounded font-medium text-foreground">
              {property.area}m²
            </div>
          </div>

          <div className="flex items-end justify-between pt-3 border-t border-border">
            <div>
              <p className="text-xs text-muted-foreground mb-0.5">Aluguel / mês</p>
              <p className="text-lg font-bold text-primary">R$ {property.price.toLocaleString("pt-BR")}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}