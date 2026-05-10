import {
  Map,
  MapMarker,
  MarkerContent,
  MarkerPopup,
  MarkerTooltip,
  MapControls
} from "@/components/ui/map";
import { Card } from "@/components/ui/card";

const locations = [
  {
    id: 1,
    name: "esp32_01",
    lng: 107.768929,
    lat: -6.932775,
  }
];

export function MyMap() {
  return (
    <Card className="h-80 p-0 overflow-hidden w-full">
      <Map center={[107.768929, -6.932775]} 
            zoom={10}
            theme="light">
            {locations.map((location) => (
                <MapMarker
                    key={location.id}
                    longitude={location.lng}
                    latitude={location.lat}
                >
                    <MarkerContent>
                        <div className="bg-red-700 size-6 rounded-full border-2 border-white shadow-lg" />
                    </MarkerContent>
                    <MarkerTooltip>{location.name}</MarkerTooltip>
                    <MarkerPopup>
                    <div className="space-y-1">
                        <p className="text-foreground font-medium font-mono">{location.name}</p>
                        <p className="text-muted-foreground text-xs font-mono">
                        {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                        </p>
                    </div>
                    </MarkerPopup>
                </MapMarker>
        ))}
        <MapControls showCompass={true}/>
      </Map>
    </Card>
  );
}