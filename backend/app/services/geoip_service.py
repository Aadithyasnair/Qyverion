import hashlib


class GeoIPService:
    """
    GeoIP lookup service. Resolves IP addresses to Latitude, Longitude, and Country Name.
    Uses deterministic hashing mapping for public IPs, and redirects RFC 1918 to sensor location.
    """

    @staticmethod
    def resolve_ip(ip_address: str) -> dict:
        """
        Returns a dictionary with 'lat', 'lon', and 'country'.
        """
        if not ip_address:
            return {"lat": 37.7749, "lon": -122.4194, "country": "Internal Sensor Target"}

        # Detect private / loopback IP address ranges
        if ip_address.startswith(("127.", "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.3")):
            return {"lat": 37.7749, "lon": -122.4194, "country": "Internal Private Segment"}

        # Generate MD5 hash integer from IP string
        h = int(hashlib.md5(ip_address.encode("utf-8")).hexdigest(), 16)

        # Diverse list of international locations
        locations = [
            {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom"},
            {"lat": 35.6762, "lon": 139.6503, "country": "Japan"},
            {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
            {"lat": 48.8566, "lon": 2.3522, "country": "France"},
            {"lat": -22.9068, "lon": -43.1729, "country": "Brazil"},
            {"lat": 55.7558, "lon": 37.6173, "country": "Russia"},
            {"lat": 30.0444, "lon": 31.2357, "country": "Egypt"},
            {"lat": -26.2041, "lon": 28.0473, "country": "South Africa"},
            {"lat": 45.4215, "lon": -75.6972, "country": "Canada"},
            {"lat": 19.4326, "lon": -99.1332, "country": "Mexico"},
            {"lat": 28.6139, "lon": 77.2090, "country": "India"},
            {"lat": 39.9042, "lon": 116.4074, "country": "China"},
            {"lat": 52.5200, "lon": 13.4050, "country": "Germany"},
            {"lat": -34.6037, "lon": -58.3816, "country": "Argentina"},
            {"lat": 1.3521, "lon": 103.8198, "country": "Singapore"}
        ]

        # Deterministically resolve model index
        loc = locations[h % len(locations)]

        # Apply a minor coordinate jitter to distinguish multi-attacker nodes
        jitter_lat = ((h % 100) - 50) / 25.0
        jitter_lon = (((h >> 8) % 100) - 50) / 25.0

        return {
            "lat": round(loc["lat"] + jitter_lat, 4),
            "lon": round(loc["lon"] + jitter_lon, 4),
            "country": loc["country"]
        }
