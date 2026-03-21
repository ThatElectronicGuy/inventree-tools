from common.models import ParameterTemplate
from part.models import PartCategory, PartCategoryParameterTemplate

CATEGORY_MAP = {
    "Cables, Wires": [
        "Datasheet URL", "Manufacturer", "Number of Cores", "Core Section",
        "Rated Voltage", "Operating Temperature", "Insulation Colour",
        "Wire Insulation Material", "Core Structure", "Kind of Core",
        "Cable Structure", "Cable External Diameter", "Package Contents",
        "Flexibility Class", "CPR Standard", "Type of Wire", "Kind of Wire",
        "Resistance To", "Cable Features", "Kind of Material",
    ],

    "Connectors/WAGO": [
        "Datasheet URL", "Manufacturer", "Current Rating", "Rated Voltage",
        "Number of Positions", "Pitch", "Mounting Type", "Core Section",
    ],

    "Connectors/Ferrules - Tulejki": [
        "Datasheet URL", "Manufacturer", "Core Section", "Insulation Colour",
        "Package", "Mounting Type",
    ],

    "Connectors/Ferrules - Tulejki/Isolated": [
        "Datasheet URL", "Manufacturer", "Core Section", "Insulation Colour",
        "Package", "Mounting Type",
    ],

    "Connectors/Ferrules - Tulejki/Non-isolated": [
        "Datasheet URL", "Manufacturer", "Core Section", "Package", "Mounting Type",
    ],

    "Connectors/Pin Header": [
        "Datasheet URL", "Manufacturer", "Number of Positions", "Pitch",
        "Current Rating", "Rated Voltage", "Mounting Type", "Package",
    ],

    "Connectors/Metal Clips": [
        "Datasheet URL", "Manufacturer", "Current Rating", "Rated Voltage",
        "Mounting Type", "Package",
    ],

    "Connectors/Plastic Clips": [
        "Datasheet URL", "Manufacturer", "Mounting Type", "Package",
    ],

    "Connectors/Power Plugs": [
        "Datasheet URL", "Manufacturer", "Current Rating", "Rated Voltage",
        "Number of Positions", "Mounting Type", "Package",
    ],

    "Resistors": [
        "Datasheet URL", "Manufacturer", "Resistance", "Tolerance", "Power",
        "Package", "Mounting Type", "Temperature Coefficient",
        "Operating Temperature", "Rated Voltage",
    ],

    "Capacitors": [
        "Datasheet URL", "Manufacturer", "Capacitance", "Tolerance",
        "Rated Voltage", "Package", "Mounting Type", "Dielectric",
        "Operating Temperature",
    ],

    "IC/Operational Amplifiers": [
        "Datasheet URL", "Manufacturer", "Package", "Mounting Type",
        "Number of Pins", "Number of Channels", "Input Offset Voltage",
        "Slew Rate", "Gain Bandwidth Product", "Supply Voltage",
        "Operating Temperature",
    ],

    "Semiconductors/Diodes": [
        "Datasheet URL", "Manufacturer", "Forward Voltage", "Current Rating",
        "Rated Voltage", "Package", "Mounting Type", "Operating Temperature",
    ],

    "Semiconductors/Diodes/Schottky": [
        "Datasheet URL", "Manufacturer", "Forward Voltage", "Current Rating",
        "Rated Voltage", "Package", "Mounting Type", "Operating Temperature",
    ],

    "Semiconductors/Diodes/Zener": [
        "Datasheet URL", "Manufacturer", "Forward Voltage", "Current Rating",
        "Rated Voltage", "Package", "Mounting Type", "Operating Temperature",
    ],

    "Semiconductors/Transistors": [
        "Datasheet URL", "Manufacturer", "Current Rating", "Package",
        "Mounting Type", "Operating Temperature",
    ],

    "Semiconductors/Transistors/BJT": [
        "Datasheet URL", "Manufacturer", "Collector Current",
        "Collector Emitter Voltage", "Package", "Mounting Type",
        "Operating Temperature",
    ],

    "Semiconductors/Transistors/MOSFETs": [
        "Datasheet URL", "Manufacturer", "Current Rating",
        "Drain Source Voltage", "Gate Threshold Voltage", "Rds On",
        "Package", "Mounting Type", "Operating Temperature",
    ],

    "Mechanical/Knobs": [
        "Datasheet URL", "Manufacturer", "Mounting Type", "Package",
    ],

    "Mechanical/Switches": [
        "Datasheet URL", "Manufacturer", "Switch Type", "Number of Positions",
        "Current Rating", "Rated Voltage", "Mounting Type", "Package",
    ],

    "Mechanical/Transformers": [
        "Datasheet URL", "Manufacturer", "Transformer Type",
        "Primary Voltage", "Secondary Voltage", "Current Rating",
        "Mounting Type", "Package",
    ],

    "Oscillators/Quartz": [
        "Datasheet URL", "Manufacturer", "Frequency", "Package",
        "Mounting Type", "Operating Temperature",
    ],

    "Oscillators/Oscillators": [
        "Datasheet URL", "Manufacturer", "Frequency", "Package",
        "Mounting Type", "Rated Voltage", "Operating Temperature",
    ],

    "Oscillators/Generators": [
        "Datasheet URL", "Manufacturer", "Frequency", "Package",
        "Mounting Type", "Rated Voltage", "Operating Temperature",
    ],
}

print("=== APPLY CATEGORY TEMPLATE MATRIX ===")

for category_path, template_names in CATEGORY_MAP.items():
    cat = PartCategory.objects.filter(pathstring=category_path).first()

    if not cat:
        print(f"[BRAK KATEGORII] {category_path}")
        continue

    print(f"\nKATEGORIA: {category_path}")

    existing = {
        rel.template.name: rel
        for rel in PartCategoryParameterTemplate.objects.filter(category=cat).select_related("template")
    }

    wanted = set(template_names)

    for name in template_names:
        tpl = ParameterTemplate.objects.filter(name=name).first()
        if not tpl:
            print(f"  [BRAK TEMPLATE] {name}")
            continue

        obj, created = PartCategoryParameterTemplate.objects.get_or_create(
            category=cat,
            template=tpl,
            defaults={"default_value": ""}
        )

        if created:
            print(f"  [DODANO] {name}")
        else:
            print(f"  [JEST] {name}")

    # opcjonalnie: pokaż nadmiarowe przypięcia
    extra = sorted(set(existing.keys()) - wanted)
    for name in extra:
        print(f"  [NADMIAROWE - zostawione] {name}")

print("\nDONE")
