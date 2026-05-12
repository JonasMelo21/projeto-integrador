import { Heart, Bed, Bath, MapPin } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";

interface DisplayProperty {
  id: string;
  title: string;
  location: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  area: number;
  image: string;
  mlTag: "Preço Justo" | "Oportunidade";
  images: string[];
  description: string;
  priceComparison: number;
  amenities: string[];
}

interface PropertyCardProps {
  property: DisplayProperty;
}

export function PropertyCard({ property }: PropertyCardProps) {
  const [isFavorite, setIsFavorite] = useState(false);
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/property/${property.id}`)}
      className="bg-card rounded-xl overflow-hidden border border-border hover:shadow-xl transition-all cursor-pointer group"
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
          className="absolute top-3 right-3 p-2 bg-white/90 rounded-full hover:bg-white transition-all shadow-md"
        >
          <Heart
            className={`w-5 h-5 ${
              isFavorite ? "fill-red-500 text-red-500" : "text-gray-600"
            }`}
          />
        </button>
        <div className="absolute top-3 left-3">
          <span
            className={`px-3 py-1 rounded-full text-xs shadow-md ${
              property.mlTag === "Preço Justo"
                ? "bg-success text-success-foreground"
                : "bg-warning text-warning-foreground"
            }`}
          >
            {property.mlTag}
          </span>
        </div>
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="flex-1 line-clamp-1">{property.title}</h3>
        </div>

        <div className="flex items-center gap-1 text-muted-foreground mb-3 text-sm">
          <MapPin className="w-4 h-4" />
          <span className="line-clamp-1">{property.location}</span>
        </div>

        <div className="flex items-center gap-4 mb-3 text-muted-foreground text-sm">
          <div className="flex items-center gap-1">
            <Bed className="w-4 h-4" />
            <span>{property.bedrooms}</span>
          </div>
          <div className="flex items-center gap-1">
            <Bath className="w-4 h-4" />
            <span>{property.bathrooms}</span>
          </div>
          <div className="text-xs bg-secondary px-2 py-1 rounded">
            {property.area}m²
          </div>
        </div>

        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs text-muted-foreground">Aluguel</p>
            <p className="text-primary">R$ {property.price.toLocaleString()}/mês</p>
          </div>
        </div>
      </div>
    </div>
  );
}
