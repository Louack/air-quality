import pytest
from django.db.models import F, FloatField
from apps.air_quality.conversions import get_qs_with_converted_concentration
from apps.air_quality.models import AirCompoundReading
from apps.air_quality.tests.factories import AirCompoundReadingFactory, CompoundFactory


@pytest.mark.django_db
class TestConcentrationConversions:
    """Test suite for concentration unit conversions."""

    @pytest.fixture
    def gaseous_compound(self):
        """Create a gaseous compound for testing."""
        return CompoundFactory(
            full_name="Carbon Monoxide",
            symbol="CO",
            is_gaseous=True,
            molecular_weight=28.01
        )

    @pytest.fixture
    def non_gaseous_compound(self):
        """Create a non-gaseous compound for testing."""
        return CompoundFactory(
            full_name="Lead",
            symbol="Pb",
            is_gaseous=False,
            molecular_weight=207.2
        )

    def test_same_unit_conversion(self, gaseous_compound):
        """Test that conversion between same units returns original value."""
        original_value = 42.0
        for unit in ["ug_m3", "mg_m3", "ppm", "ppb"]:
            reading = AirCompoundReadingFactory(
                compound=gaseous_compound,
                entered_concentration_unit=unit,
                entered_concentration_value=original_value
            )
            qs = reading.__class__.objects.filter(pk=reading.pk)
            converted = get_qs_with_converted_concentration(qs, unit)
            assert converted.first().concentration_value == original_value

    @pytest.mark.parametrize("from_unit,to_unit,value,expected", [
        ("ug_m3", "mg_m3", 1000.0, 1.0),  # 1000 µg/m³ = 1 mg/m³
        ("mg_m3", "ug_m3", 1.0, 1000.0),  # 1 mg/m³ = 1000 µg/m³
        ("ppm", "ppb", 1.0, 1000.0),      # 1 ppm = 1000 ppb
        ("ppb", "ppm", 1000.0, 1.0),      # 1000 ppb = 1 ppm
    ])
    def test__unit_conversions_without_molecular_weight(self, gaseous_compound, from_unit, to_unit, value, expected):
        """Test unit conversions that don't require molecular weight."""
        reading = AirCompoundReadingFactory(
            compound=gaseous_compound,
            entered_concentration_unit=from_unit,
            entered_concentration_value=value
        )
        qs = reading.__class__.objects.filter(pk=reading.pk)
        converted = get_qs_with_converted_concentration(qs, to_unit)
        assert abs(converted.first().concentration_value - expected) < 0.0001

    def test_gas_concentration_conversions(self, gaseous_compound):
        """Test conversions between mass and volume concentrations for gases."""
        # Test conversion from ppm to mg/m³ for CO (MW = 28.01 g/mol)
        # Using the formula: mg/m³ = (ppm * MW) / 24.45
        reading = AirCompoundReadingFactory(
            compound=gaseous_compound,  # CO
            entered_concentration_unit="ppm",
            entered_concentration_value=1.0  # 1 ppm
        )
        qs = reading.__class__.objects.filter(pk=reading.pk)
        
        # Convert to mg/m³
        converted = get_qs_with_converted_concentration(qs, "mg_m3")
        expected_mg_m3 = (1.0 * 28.01) / 24.45
        assert abs(converted.first().concentration_value - expected_mg_m3) < 0.0001

        # Convert to µg/m³
        converted = get_qs_with_converted_concentration(qs, "ug_m3")
        expected_ug_m3 = expected_mg_m3 * 1000
        assert abs(converted.first().concentration_value - expected_ug_m3) < 0.0001

    def test_non_gaseous_compound_conversions(self, non_gaseous_compound):
        """Test that volume concentration conversions are not allowed for non-gaseous compounds."""
        reading = AirCompoundReadingFactory(
            compound=non_gaseous_compound,
            entered_concentration_unit="ug_m3",
            entered_concentration_value=100.0
        )
        qs = reading.__class__.objects.filter(pk=reading.pk)

        # Mass-to-mass conversion should work
        mass_converted = get_qs_with_converted_concentration(qs, "mg_m3")
        assert mass_converted.first().concentration_value == 0.1  # 100 µg/m³ = 0.1 mg/m³

        # Mass-to-volume conversion should return None
        volume_converted = get_qs_with_converted_concentration(qs, "ppm")
        assert volume_converted.first().concentration_value is None

    @pytest.mark.parametrize("from_unit,to_unit,value,compound_attrs,expected", [
        # CO (MW = 28.01): 1 ppm = 1.15 mg/m³
        ("ppm", "mg_m3", 1.0, 
         {"molecular_weight": 28.01, "is_gaseous": True}, 1.15),
        # NO2 (MW = 46.01): 1 ppm = 1.88 mg/m³
        ("ppm", "mg_m3", 1.0,
         {"molecular_weight": 46.01, "is_gaseous": True}, 1.88),
        # SO2 (MW = 64.06): 100 ppb = 0.262 mg/m³
        ("ppb", "mg_m3", 100.0,
         {"molecular_weight": 64.06, "is_gaseous": True}, 0.26),
    ])
    def test_specific_compound_conversions(self, from_unit, to_unit, value,
                                         compound_attrs, expected):
        """Test conversions for specific compounds with different molecular weights."""
        compound = CompoundFactory(**compound_attrs)
        reading = AirCompoundReadingFactory(
            compound=compound,
            entered_concentration_unit=from_unit,
            entered_concentration_value=value
        )
        qs = reading.__class__.objects.filter(pk=reading.pk)
        converted = get_qs_with_converted_concentration(qs, to_unit)

        assert round(converted.first().concentration_value, 2) == expected
