from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# 1. Setup Client and Model
client = QdrantClient(path="./qdrant_storage") # Local disk mode
model = SentenceTransformer('all-MiniLM-L6-v2') # Same as router

# 2. Create Collection
client.recreate_collection(
    collection_name="products",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 3. Prepare Product Data
products = [
    {
        "id": 1,
        "name": "Industrial Pump PX-500",
        "description": "High-pressure hydraulic pump for heavy industrial use, features a stainless steel casing and vibration reduction technology.",
        "price": "$1,200",
        "specs_pdf": "https://yourserver.com/docs/px500_specs.pdf"
    },
    {
        "id": 2,
        "name": "Compact Solar Panel Z-10",
        "description": "Portable 100W monocrystalline solar panel with weather-resistant ETFE coating and dual USB-C output ports.",
        "price": "$250",
        "specs_pdf": "https://yourserver.com/docs/z10_solar.pdf"
    },
    {
        "id": 3,
        "name": "Thermal Imaging Camera T-90",
        "description": "Handheld infrared sensor for electrical inspections and heat leak detection. Includes a 3.5-inch LCD display.",
        "price": "$850",
        "specs_pdf": "https://yourserver.com/docs/t90_thermal.pdf"
    },
    {
        "id": 4,
        "name": "Heavy-Duty Electric Drill D-Force",
        "description": "Cordless 20V brushless motor drill with variable speed control and high-torque performance for masonry and steel.",
        "price": "$185",
        "specs_pdf": "https://yourserver.com/docs/dforce_drill.pdf"
    },
    {
        "id": 5,
        "name": "Digital Multimeter Pro-Flux",
        "description": "Auto-ranging digital tester for voltage, current, and resistance. True RMS certified for precision electrical work.",
        "price": "$120",
        "specs_pdf": "https://yourserver.com/docs/proflux_meter.pdf"
    },
    {
        "id": 6,
        "name": "Ultrasonic Flow Meter U-Flow",
        "description": "Non-invasive liquid flow sensor using ultrasonic waves. Perfect for measuring water and chemical flow in pipes.",
        "price": "$2,100",
        "specs_pdf": "https://yourserver.com/docs/uflow_meter.pdf"
    },
    {
        "id": 7,
        "name": "Backup Battery Station PowerBank-X",
        "description": "2000Wh portable power station with AC outlets. Designed for emergency backup or remote worksite electricity.",
        "price": "$1,500",
        "specs_pdf": "https://yourserver.com/docs/powerbankx.pdf"
    },
    {
        "id": 8,
        "name": "Smart Thermostat Nexus-V",
        "description": "WiFi-enabled climate control system for industrial warehouses. Optimizes HVAC usage based on occupancy.",
        "price": "$310",
        "specs_pdf": "https://yourserver.com/docs/nexusv_thermostat.pdf"
    },
    {
        "id": 9,
        "name": "Laser Leveler CrossLine-360",
        "description": "Self-leveling 360-degree green beam laser for construction alignment and precision tiling.",
        "price": "$220",
        "specs_pdf": "https://yourserver.com/docs/crossline_laser.pdf"
    },
    {
        "id": 10,
        "name": "Safety Air Compressor AC-Low",
        "description": "Ultra-quiet 6-gallon air compressor with oil-free pump and reinforced safety valves for workshop use.",
        "price": "$450",
        "specs_pdf": "https://yourserver.com/docs/aclow_compressor.pdf"
    }
]

# 4. Upsert to Qdrant
points = []
for p in products:
    vector = model.encode(p["description"]).tolist()
    points.append(PointStruct(
        id=p["id"],
        vector=vector,
        payload={
            "name": p["name"],
            "description": p["description"],
            "price": p["price"],
            "specs_pdf": p["specs_pdf"]
        }
    ))

client.upsert(collection_name="products", points=points)
print("Product database initialized!")
