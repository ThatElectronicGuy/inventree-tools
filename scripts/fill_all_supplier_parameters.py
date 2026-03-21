import os
import re
import yaml
from django.contrib.contenttypes.models import ContentType

from common.models import Parameter
from part.models import Part, PartCategoryParameterTemplate
from company.models import SupplierPart

from inventree_part_import.suppliers.supplier_tme import TMEApi
from inventree_part_import.suppliers.supplier_digikey import DigiKey
from inventree_part_import.suppliers.supplier_mouser import Mouser


DRY_RUN = False
ONLY_PART_ID = None
ONLY_CATEGORY = None
ONLY_SUPPLIER = None   # "TME", "DigiKey", "Mouser" albo None

PART_CT = ContentType.objects.get_for_model(Part)

PARAM_ALIASES = {
    # wspólne
    "manufacturer": "Manufacturer",
    "package": "Package",
    "case": "Package",
    "mounting": "Mounting Type",
    "mounting type": "Mounting Type",
    "rated voltage": "Rated Voltage",
    "voltage rating": "Rated Voltage",
    "operating temperature": "Operating Temperature",
    "current": "Current Rating",
    "current rating": "Current Rating",

    # kable
    "number of cores": "Number of Cores",
    "core section": "Core Section",
    "wire gauge": "Core Section",
    "core diameter": "Core Section",
    "insulation colour": "Insulation Colour",
    "insulation color": "Insulation Colour",
    "wire insulation material": "Wire Insulation Material",
    "insulation material": "Wire Insulation Material",
    "core structure": "Core Structure",
    "kind of core": "Kind of Core",
    "cable structure": "Cable Structure",
    "cable external diameter": "Cable External Diameter",
    "outside diameter": "Cable External Diameter",
    "package contents": "Package Contents",
    "flexibility class": "Flexibility Class",
    "cpr standard": "CPR Standard",
    "type of wire": "Type of Wire",
    "kind of wire": "Kind of Wire",
    "resistance to": "Resistance To",
    "cable features": "Cable Features",
    "kind of material": "Kind of Material",
    "cable type": "Type of Wire",
    "conductor material": "Kind of Core",
    "jacket (insulation) material": "Wire Insulation Material",
    "jacket (insulation) diameter": "Cable External Diameter",
    "jacket color": "Insulation Colour",
    "voltage": "Rated Voltage",
    "features": "Cable Features",
    "size": "Core Section",
    "number of wire entries": "Number of Positions",
    "number of terminals": "Number of Positions",
    "termination": "Mounting Type",
    "electrical mounting": "Mounting Type",
    "mechanical mounting": "Mounting Type",
    "wire cross-section": "Core Section",
    "cable type": "Type of Wire",
    "conductor material": "Kind of Core",
    "jacket (insulation) material": "Wire Insulation Material",
    "jacket (insulation) diameter": "Cable External Diameter",
    "jacket color": "Insulation Colour",
    "voltage": "Rated Voltage",
    "features": "Cable Features",
    "size": "Core Section",

    # rezystory
    "resistance": "Resistance",
    "resistance (ohms)": "Resistance",
    "tolerance": "Tolerance",
    "power": "Power",
    "power (watts)": "Power",
    "temperature coefficient": "Temperature Coefficient",

    # kondensatory
    "capacitance": "Capacitance",
    "dielectric": "Dielectric",

    # ic/opamp
    "number of pins": "Number of Pins",
    "number of channels": "Number of Channels",
    "channels per chip": "Number of Channels",
    "input offset voltage": "Input Offset Voltage",
    "slew rate": "Slew Rate",
    "gain bandwidth": "Gain Bandwidth Product",
    "gain bandwidth product": "Gain Bandwidth Product",
    "supply voltage": "Supply Voltage",
    "supply voltage - min": "Supply Voltage",
    "supply voltage - max": "Supply Voltage",

    # diody / tranzystory
    "forward voltage": "Forward Voltage",
    "collector current": "Collector Current",
    "collector-emitter voltage": "Collector Emitter Voltage",
    "collector emitter voltage": "Collector Emitter Voltage",
    "drain-source voltage": "Drain Source Voltage",
    "drain source voltage": "Drain Source Voltage",
    "gate threshold voltage": "Gate Threshold Voltage",
    "rds(on)": "Rds On",
    "drain-source on resistance": "Rds On",
    "drain source on resistance": "Rds On",

    # złącza
    "number of positions": "Number of Positions",
    "positions": "Number of Positions",
    "pitch": "Pitch",

    # mechanika
    "switch type": "Switch Type",
    "transformer type": "Transformer Type",
    "primary voltage": "Primary Voltage",
    "secondary voltage": "Secondary Voltage",

    # oscylatory
    "frequency": "Frequency",
}

UNMAPPED_LOG = True


def clean_html(text):
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


def norm_key(text):
    return clean_html(text).strip().lower()


def append_value(result, key, value):
    value = clean_html(value)
    if not value:
        return

    if key in result and result[key]:
        parts = result[key].split(" / ")
        if value not in parts:
            result[key] += " / " + value
    else:
        result[key] = value


def get_category_chain(category):
    chain = []
    c = category
    while c is not None:
        chain.append(c)
        c = getattr(c, "parent", None)
    return list(reversed(chain))


def get_template_map_for_part(part):
    chain = get_category_chain(part.category)
    cat_templates = []

    for cat in chain:
        cat_templates.extend(
            list(
                PartCategoryParameterTemplate.objects
                .filter(category=cat)
                .select_related("template")
            )
        )

    return {ct.template.name: ct.template for ct in cat_templates}


def upsert_parameters_for_part(part, mapped):
    template_map = get_template_map_for_part(part)

    print(f"\nPART {part.pk}: {part.name}")
    print("CATEGORY:", part.category.pathstring if part.category else None)
    print("FOUND TEMPLATES:", sorted(template_map.keys()))
    print("MAPPED:", mapped)

    for key, value in mapped.items():
        tpl = template_map.get(key)

        if not tpl:
            print(f"  [SKIP TEMPLATE] {key}")
            continue

        obj = Parameter.objects.filter(
            model_type=PART_CT,
            model_id=part.pk,
            template=tpl
        ).first()

        if obj:
            current = clean_html(obj.data or "")
            if current:
                print(f"  [EXISTS] {key} = {current}")
                continue

            if DRY_RUN:
                print(f"  [DRY UPDATE] {key} = {value}")
            else:
                obj.data = value
                obj.save()
                print(f"  [UPDATED] {key} = {value}")
        else:
            if DRY_RUN:
                print(f"  [DRY CREATE] {key} = {value}")
            else:
                Parameter.objects.create(
                    model_type=PART_CT,
                    model_id=part.pk,
                    template=tpl,
                    data=value,
                )
                print(f"  [CREATED] {key} = {value}")


def load_configs():
    with open('/root/.config/inventree_part_import/suppliers.yaml', 'r', encoding='utf-8') as f:
        suppliers_cfg = yaml.safe_load(f)

    with open('/root/.config/inventree_part_import/config.yaml', 'r', encoding='utf-8') as f:
        config_cfg = yaml.safe_load(f)

    return suppliers_cfg, config_cfg


def build_tme_api(suppliers_cfg, config_cfg):
    tme_cfg = suppliers_cfg['tme']
    return TMEApi(
        token=tme_cfg['api_token'],
        secret=tme_cfg['api_secret'],
        language=config_cfg.get('language', 'eng').upper()[:2],
        country=config_cfg.get('location', 'PL'),
        currency=config_cfg.get('currency', 'EUR'),
    )


def build_digikey_supplier(suppliers_cfg, config_cfg):
    dk_cfg = suppliers_cfg['digikey']
    s = DigiKey()
    ok = s.setup(
        client_id=dk_cfg['client_id'],
        client_secret=dk_cfg['client_secret'],
        currency=config_cfg.get('currency', 'EUR'),
        language=config_cfg.get('language', 'eng'),
        location=config_cfg.get('location', 'PL'),
        interactive_part_matches=config_cfg.get('interactive_part_matches', 10),
    )
    if not ok:
        raise RuntimeError("DigiKey setup failed")
    return s


def build_mouser_supplier(suppliers_cfg, config_cfg):
    ms_cfg = suppliers_cfg['mouser']
    s = Mouser()
    ok = s.setup(
        api_key=ms_cfg['api_key'],
        currency=config_cfg.get('currency', 'EUR'),
        scraping=config_cfg.get('scraping', True),
        browser_cookies=ms_cfg.get('browser_cookies', ''),
        locale_url=ms_cfg.get('locale_url', 'www.mouser.com'),
    )
    if not ok:
        raise RuntimeError("Mouser setup failed")
    return s


def map_api_part_to_templates(api_part):
    mapped = {}
    unmapped = []

    if getattr(api_part, "datasheet_url", None):
        mapped["Datasheet URL"] = clean_html(api_part.datasheet_url)

    if getattr(api_part, "manufacturer", None):
        mapped["Manufacturer"] = clean_html(api_part.manufacturer)

    for raw_name, raw_value in (api_part.parameters or {}).items():
        name = clean_html(raw_name)
        value = clean_html(raw_value)

        if not name or not value:
            continue

        alias = PARAM_ALIASES.get(norm_key(name))

        if alias:
            append_value(mapped, alias, value)
        else:
            unmapped.append(f"{name} = {value}")

    return mapped, unmapped


def pick_search_terms(sp):
    terms = []

    if sp.SKU:
        terms.append(sp.SKU)

    if sp.manufacturer_part:
        if sp.manufacturer_part.MPN:
            terms.append(sp.manufacturer_part.MPN)

    # usuń duplikaty, zachowaj kolejność
    dedup = []
    seen = set()
    for t in terms:
        if t and t not in seen:
            dedup.append(t)
            seen.add(t)

    return dedup


def search_with_supplier(supplier_obj, sp):
    terms = pick_search_terms(sp)
    last_error = None

    for term in terms:
        try:
            results, count = supplier_obj.search(term)
        except Exception as e:
            last_error = f"search({term}) failed: {e}"
            continue

        if not results:
            continue

        # spróbuj znaleźć najlepszy match po SKU/MPN
        sku = (sp.SKU or "").lower()
        mpn = (sp.manufacturer_part.MPN.lower() if sp.manufacturer_part and sp.manufacturer_part.MPN else "")

        for api_part in results:
            candidates = [
                clean_html(getattr(api_part, "SKU", "")).lower(),
                clean_html(getattr(api_part, "MPN", "")).lower(),
            ]
            if sku and sku in candidates:
                return api_part, f"matched by SKU via term={term}"
            if mpn and mpn in candidates:
                return api_part, f"matched by MPN via term={term}"

        # fallback: pierwszy wynik
        return results[0], f"fallback first result via term={term}, count={count}"

    return None, last_error or "no results"


def detect_supplier_backend(sp):
    supplier_name = (sp.supplier.name or "").lower()

    if "tme" in supplier_name:
        return "tme"
    if "digikey" in supplier_name or "digi-key" in supplier_name:
        return "digikey"
    if "mouser" in supplier_name:
        return "mouser"
    return None


def map_tme_supplierpart(sp, tme_api):
    symbol = sp.SKU
    if not symbol:
        return {}, ["brak SKU"]

    try:
        product = tme_api.get_product(symbol)
        params = tme_api.get_parameters(symbol)
    except Exception as e:
        return {}, [f"błąd API TME: {e}"]

    if not params:
        return {}, ["TME nie zwróciło parametrów"]

    mapped = {}

    if sp.link:
        mapped["Datasheet URL"] = sp.link
    elif product and product.get("ProductInformationPage"):
        url = product["ProductInformationPage"]
        if url.startswith("//"):
            url = "https:" + url
        mapped["Datasheet URL"] = url

    unmapped = []

    for p in params:
        raw_name = clean_html(p.get("ParameterName", ""))
        raw_value = clean_html(p.get("ParameterValue", ""))

        if not raw_name or not raw_value:
            continue

        alias = PARAM_ALIASES.get(norm_key(raw_name))

        if alias:
            append_value(mapped, alias, raw_value)
        else:
            unmapped.append(f"{raw_name} = {raw_value}")

    return mapped, unmapped


def map_digikey_supplierpart(sp, dk_supplier):
    api_part, info = search_with_supplier(dk_supplier, sp)

    if not api_part:
        return {}, [f"DigiKey: {info}"]

    mapped, unmapped = map_api_part_to_templates(api_part)
    unmapped.insert(0, f"DigiKey search info: {info}")
    return mapped, unmapped


def map_mouser_supplierpart(sp, ms_supplier):
    api_part, info = search_with_supplier(ms_supplier, sp)

    if not api_part:
        return {}, [f"Mouser: {info}"]

    try:
        api_part.finalize()
    except Exception as e:
        unmapped_extra = [f"Mouser finalize error: {e}"]
    else:
        unmapped_extra = [f"Mouser search info: {info}"]

    mapped, unmapped = map_api_part_to_templates(api_part)
    unmapped = unmapped_extra + unmapped
    return mapped, unmapped


suppliers_cfg, config_cfg = load_configs()

tme_api = build_tme_api(suppliers_cfg, config_cfg)
digikey_supplier = build_digikey_supplier(suppliers_cfg, config_cfg)
mouser_supplier = build_mouser_supplier(suppliers_cfg, config_cfg)

qs = (
    SupplierPart.objects
    .select_related("part", "manufacturer_part", "part__category", "supplier")
    .all()
)

if ONLY_PART_ID is not None:
    qs = qs.filter(part_id=ONLY_PART_ID)

if ONLY_CATEGORY is not None:
    qs = qs.filter(part__category__pathstring=ONLY_CATEGORY)

if ONLY_SUPPLIER is not None:
    qs = qs.filter(supplier__name__icontains=ONLY_SUPPLIER)

seen = set()

print("DRY_RUN:", DRY_RUN)
print("ONLY_PART_ID:", ONLY_PART_ID)
print("ONLY_CATEGORY:", ONLY_CATEGORY)
print("ONLY_SUPPLIER:", ONLY_SUPPLIER)

for sp in qs.order_by("part_id"):
    part = sp.part

    if not part:
        continue

    if part.pk in seen:
        continue
    seen.add(part.pk)

    if not part.category:
        print(f"\nSKIP part {part.pk} - brak kategorii")
        continue

    backend = detect_supplier_backend(sp)

    if backend == "tme":
        mapped, unmapped = map_tme_supplierpart(sp, tme_api)
    elif backend == "digikey":
        mapped, unmapped = map_digikey_supplierpart(sp, digikey_supplier)
    elif backend == "mouser":
        mapped, unmapped = map_mouser_supplierpart(sp, mouser_supplier)
    else:
        print(f"\nSKIP part {part.pk} - nieznany supplier backend")
        continue

    if not mapped and unmapped:
        print(f"\nPART {part.pk}: {part.name}")
        print("CATEGORY:", part.category.pathstring if part.category else None)
        print("SUPPLIER:", sp.supplier.name if sp.supplier else None)
        for line in unmapped:
            print("  [INFO]", line)
        continue

    upsert_parameters_for_part(part, mapped)

    if UNMAPPED_LOG and unmapped:
        print("  [UNMAPPED]")
        for line in unmapped:
            print("   -", line)

print("\nDONE")
