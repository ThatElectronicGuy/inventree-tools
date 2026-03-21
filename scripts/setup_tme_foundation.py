from common.models import ParameterTemplate
from part.models import PartCategory, PartCategoryParameterTemplate

TEMPLATES = {
    # wspólne
    "Datasheet URL": {"description": "Datasheet or product URL", "units": ""},
    "Manufacturer": {"description": "Manufacturer", "units": ""},
    "Package": {"description": "Package", "units": ""},
    "Mounting Type": {"description": "Mounting type", "units": ""},
    "Rated Voltage": {"description": "Rated voltage", "units": "V"},
    "Operating Temperature": {"description": "Operating temperature", "units": ""},
    "Current Rating": {"description": "Current rating", "units": "A"},

    # kable
    "Number of Cores": {"description": "Number of cores", "units": ""},
    "Core Section": {"description": "Core section", "units": "mm2"},
    "Insulation Colour": {"description": "Insulation colour", "units": ""},
    "Wire Insulation Material": {"description": "Wire insulation material", "units": ""},
    "Core Structure": {"description": "Core structure", "units": ""},
    "Kind of Core": {"description": "Kind of core", "units": ""},
    "Cable Structure": {"description": "Cable structure", "units": ""},
    "Cable External Diameter": {"description": "Cable external diameter", "units": "mm"},
    "Package Contents": {"description": "Package contents", "units": ""},
    "Flexibility Class": {"description": "Flexibility class", "units": ""},
    "CPR Standard": {"description": "CPR standard", "units": ""},
    "Type of Wire": {"description": "Type of wire", "units": ""},
    "Kind of Wire": {"description": "Kind of wire", "units": ""},
    "Resistance To": {"description": "Resistance to", "units": ""},
    "Cable Features": {"description": "Cable features", "units": ""},
    "Kind of Material": {"description": "Kind of material", "units": ""},

    # rezystory
    "Resistance": {"description": "Resistance", "units": "Ohm"},
    "Tolerance": {"description": "Tolerance", "units": "%"},
    "Power": {"description": "Power", "units": "W"},
    "Temperature Coefficient": {"description": "Temperature coefficient", "units": "ppm/C"},

    # kondensatory
    "Capacitance": {"description": "Capacitance", "units": "F"},
    "Dielectric": {"description": "Dielectric", "units": ""},

    # opamp / ic
    "Number of Pins": {"description": "Number of pins", "units": ""},
    "Number of Channels": {"description": "Number of channels", "units": ""},
    "Input Offset Voltage": {"description": "Input offset voltage", "units": "V"},
    "Slew Rate": {"description": "Slew rate", "units": "V/us"},
    "Gain Bandwidth Product": {"description": "Gain bandwidth product", "units": "Hz"},
    "Supply Voltage": {"description": "Supply voltage", "units": "V"},

    # diody / tranzystory
    "Forward Voltage": {"description": "Forward voltage", "units": "V"},
    "Collector Current": {"description": "Collector current", "units": "A"},
    "Collector Emitter Voltage": {"description": "Collector emitter voltage", "units": "V"},
    "Drain Source Voltage": {"description": "Drain source voltage", "units": "V"},
    "Gate Threshold Voltage": {"description": "Gate threshold voltage", "units": "V"},
    "Rds On": {"description": "Drain-source on resistance", "units": "Ohm"},

    # złącza
    "Number of Positions": {"description": "Number of positions", "units": ""},
    "Pitch": {"description": "Pitch", "units": "mm"},

    # mechanika
    "Switch Type": {"description": "Switch type", "units": ""},
    "Transformer Type": {"description": "Transformer type", "units": ""},
    "Primary Voltage": {"description": "Primary voltage", "units": "V"},
    "Secondary Voltage": {"description": "Secondary voltage", "units": "V"},

    # oscylatory
    "Frequency": {"description": "Frequency", "units": "Hz"},
}

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
        "Datasheet URL", "Manufacturer", "Rated Voltage",
    ],

    "Connectors/Pin Header": [
        "Datasheet URL", "Manufacturer", "Number of Positions", "Pitch",
        "Current Rating", "Rated Voltage", "Mounting Type",
    ],

    "Resistors": [
        "Datasheet URL", "Manufacturer", "Resistance", "Tolerance", "Power",
        "Package", "Mounting Type", "Temperature Coefficient",
        "Operating Temperature",
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

    "Semiconductors/Diodes/Schottky": [
        "Datasheet URL", "Manufacturer", "Forward Voltage", "Current Rating",
        "Rated Voltage", "Package", "Mounting Type", "Operating Temperature",
    ],

    "Semiconductors/Diodes/Zener": [
        "Datasheet URL", "Manufacturer", "Forward Voltage", "Current Rating",
        "Rated Voltage", "Package", "Mounting Type", "Operating Temperature",
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

    "Mechanical/Switches": [
        "Datasheet URL", "Manufacturer", "Switch Type", "Number of Positions",
        "Current Rating", "Rated Voltage", "Mounting Type",
    ],

    "Mechanical/Transformers": [
        "Datasheet URL", "Manufacturer", "Transformer Type",
        "Primary Voltage", "Secondary Voltage", "Current Rating",
        "Mounting Type",
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

print("=== TWORZENIE / AKTUALIZACJA TEMPLATEK ===")
for name, meta in TEMPLATES.items():
    obj, created = ParameterTemplate.objects.get_or_create(
        name=name,
        defaults={
            "description": meta["description"],
            "units": meta["units"],
        }
    )

    if created:
        print(f"[CREATE TEMPLATE] {name}")
    else:
        changed = False
        if obj.description != meta["description"]:
            obj.description = meta["description"]
            changed = True
        if obj.units != meta["units"]:
            obj.units = meta["units"]
            changed = True
        if changed:
            obj.save()
            print(f"[UPDATE TEMPLATE] {name}")
        else:
            print(f"[OK TEMPLATE] {name}")

print("\n=== PODPINANIE DO KATEGORII ===")
for category_path, template_names in CATEGORY_MAP.items():
    cat = PartCategory.objects.filter(pathstring=category_path).first()

    if not cat:
        print(f"[BRAK KATEGORII] {category_path}")
        continue

    print(f"\nKATEGORIA: {category_path}")

    for template_name in template_names:
        tpl = ParameterTemplate.objects.filter(name=template_name).first()

        if not tpl:
            print(f"  [BRAK TEMPLATE] {template_name}")
            continue

        obj, created = PartCategoryParameterTemplate.objects.get_or_create(
            category=cat,
            template=tpl,
            defaults={"default_value": ""}
        )

        if created:
            print(f"  [DODANO] {template_name}")
        else:
            print(f"  [JEST] {template_name}")

print("\nDONE")
