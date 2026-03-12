from part.models import Part

# Znajdź najwyższy istniejący numeryczny IPN
max_ipn = 30040

for part in Part.objects.exclude(IPN__isnull=True).exclude(IPN=""):
    try:
        ipn = int(part.IPN)
        if ipn > max_ipn:
            max_ipn = ipn
    except (ValueError, TypeError):
        pass

start_ipn = max_ipn + 1

# Znajdź wszystkie party bez IPN
parts_without_ipn = Part.objects.filter(IPN__isnull=True) | Part.objects.filter(IPN="")
parts_without_ipn = parts_without_ipn.order_by("pk").distinct()

print(f"Najwyższy istniejący IPN: {max_ipn}")
print(f"Start numeracji od: {start_ipn}")
print(f"Parts without IPN: {parts_without_ipn.count()}")

current_ipn = start_ipn

for part in parts_without_ipn:
    print(f"{part.pk} | {part.name} -> {current_ipn}")
    part.IPN = str(current_ipn)
    part.save(update_fields=["IPN"])
    current_ipn += 1

print("Gotowe.")