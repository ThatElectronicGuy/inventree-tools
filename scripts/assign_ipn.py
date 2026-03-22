from part.models import Part

START_IPN = 30000
DRY_RUN = False


def parse_ipn(value):
    try:
        value = str(value).strip()
        if not value:
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def get_used_ipns():
    used = set()

    for part in Part.objects.exclude(IPN__isnull=True).exclude(IPN=""):
        ipn_num = parse_ipn(part.IPN)
        if ipn_num is not None and ipn_num >= START_IPN:
            used.add(ipn_num)

    return used


def generate_free_ipns(used, count):
    free = []
    candidate = START_IPN

    while len(free) < count:
        if candidate not in used:
            free.append(candidate)
        candidate += 1

    return free


parts_without_ipn = list(
    Part.objects.filter(IPN__isnull=True) | Part.objects.filter(IPN="")
)
parts_without_ipn = sorted(parts_without_ipn, key=lambda p: p.pk)

used_ipns = get_used_ipns()
free_ipns = generate_free_ipns(used_ipns, len(parts_without_ipn))

print(f"START_IPN = {START_IPN}")
print(f"MAX USED IPN = {max(used_ipns) if used_ipns else 'BRAK'}")
print(f"Partów bez IPN: {len(parts_without_ipn)}")
print(f"DRY_RUN = {DRY_RUN}")
print()

for part, new_ipn in zip(parts_without_ipn, free_ipns):
    print(f"PART pk={part.pk} name={part.name} -> IPN {new_ipn}")

    if not DRY_RUN:
        part.IPN = str(new_ipn)
        part.save(update_fields=["IPN"])

print("\nDONE")
