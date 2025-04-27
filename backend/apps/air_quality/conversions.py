from django.db.models import Case, ExpressionWrapper, F, FloatField, When

CONVERSION_RULES = {
    ("ug_m3", "ug_m3"): lambda: F("entered_concentration_value"),
    ("ug_m3", "mg_m3"): lambda: F("entered_concentration_value") / 1000,
    ("ug_m3", "ppm"): lambda: F("entered_concentration_value")
    * F("compound__molecular_weight")
    / 24.45
    / 1000,
    ("ug_m3", "ppb"): lambda: F("entered_concentration_value")
    * F("compound__molecular_weight")
    / 24.45,
    ("mg_m3", "mg_m3"): lambda: F("entered_concentration_value"),
    ("mg_m3", "ug_m3"): lambda: F("entered_concentration_value") * 1000,
    ("mg_m3", "ppm"): lambda: F("entered_concentration_value")
    * 24.45
    / F("compound__molecular_weight"),
    ("mg_m3", "ppb"): lambda: F("entered_concentration_value")
    * 1000
    * 24.45
    / F("compound__molecular_weight"),
    ("ppm", "ppm"): lambda: F("entered_concentration_value"),
    ("ppm", "ppb"): lambda: F("entered_concentration_value") * 1000,
    ("ppm", "mg_m3"): lambda: F("entered_concentration_value")
    * F("compound__molecular_weight")
    / 24.45,
    ("ppm", "ug_m3"): lambda: F("entered_concentration_value")
    * F("compound__molecular_weight")
    / 24.45
    * 1000,
    ("ppb", "ppb"): lambda: F("entered_concentration_value"),
    ("ppb", "ppm"): lambda: F("entered_concentration_value") / 1000,
    ("ppb", "mg_m3"): lambda: F("entered_concentration_value")
    / 1000
    * F("compound__molecular_weight")
    / 24.45,
    ("ppb", "ug_m3"): lambda: F("entered_concentration_value")
    * F("compound__molecular_weight")
    / 24.45,
}
"""
Dictionary mapping concentration unit conversion rules.
"""


def get_qs_with_converted_concentration(queryset, target_unit):
    """
    Annotates queryset with concentration values converted to target unit.
    """
    whens = []
    for (from_unit, to_unit), expression in CONVERSION_RULES.items():
        if target_unit != to_unit:
            continue

        condition_kwargs = {"entered_concentration_unit": from_unit}

        gas_check_required = (
            any(unit in ("ppm", "ppb") for unit in (from_unit, to_unit))
            and from_unit != to_unit
        )
        if gas_check_required:
            condition_kwargs["compound__is_gaseous"] = True

        whens.append(
            When(
                **condition_kwargs,
                then=ExpressionWrapper(expression(), output_field=FloatField()),
            )
        )

    return queryset.annotate(
        **{
            f"concentration_value": Case(
                *whens, default=None, output_field=FloatField()
            )
        }
    )
