[out:json][timeout:300];
area(3600076469)->.marseille;
way(area.marseille)["highway"~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|residential|living_street|pedestrian)$"];
out body geom qt;
