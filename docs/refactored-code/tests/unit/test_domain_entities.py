from datetime import datetime, timedelta

import pytest

from src.domain.entities.checkpoint import Checkpoint
from src.domain.entities.unit import Unit
from src.domain.value_objects.checkpoint_data import CheckpointData
from src.domain.value_objects.tracking_id import TrackingId
from src.domain.value_objects.unit_status import UnitStatus


class TestTrackingId:
    """Tests para el value object TrackingId"""

    def test_valid_tracking_id(self):
        """Test para tracking ID válido"""
        tracking_id = TrackingId("ABC123")
        assert str(tracking_id) == "ABC123"

    def test_empty_tracking_id_raises_error(self):
        """Test que tracking ID vacío lanza error"""
        with pytest.raises(ValueError, match="Tracking ID no puede estar vacío"):
            TrackingId("")

    def test_short_tracking_id_raises_error(self):
        """Test que tracking ID muy corto lanza error"""
        with pytest.raises(
            ValueError, match="Tracking ID debe tener al menos 3 caracteres"
        ):
            TrackingId("AB")

    def test_long_tracking_id_raises_error(self):
        """Test que tracking ID muy largo lanza error"""
        long_id = "A" * 51
        with pytest.raises(
            ValueError, match="Tracking ID no puede exceder 50 caracteres"
        ):
            TrackingId(long_id)

    def test_invalid_characters_raises_error(self):
        """Test que caracteres inválidos lanzan error"""
        with pytest.raises(
            ValueError,
            match="Tracking ID solo puede contener letras, números, guiones y guiones bajos",
        ):
            TrackingId("ABC@123")

    def test_tracking_id_equality(self):
        """Test para igualdad de tracking IDs"""
        id1 = TrackingId("ABC123")
        id2 = TrackingId("ABC123")
        id3 = TrackingId("XYZ789")

        assert id1 == id2
        assert id1 != id3
        assert hash(id1) == hash(id2)


class TestUnitStatus:
    """Tests para el enum UnitStatus"""

    def test_valid_statuses(self):
        """Test para estados válidos"""
        assert UnitStatus.is_valid_status("CREATED")
        assert UnitStatus.is_valid_status("DELIVERED")
        assert not UnitStatus.is_valid_status("INVALID")

    def test_status_transitions(self):
        """Test para transiciones de estado válidas"""
        assert UnitStatus.CREATED.can_transition_to(UnitStatus.PICKED_UP)
        assert UnitStatus.PICKED_UP.can_transition_to(UnitStatus.IN_TRANSIT)
        assert not UnitStatus.CREATED.can_transition_to(UnitStatus.DELIVERED)

    def test_delivered_is_final_state(self):
        """Test que DELIVERED es estado final"""
        next_statuses = UnitStatus.get_next_valid_statuses(UnitStatus.DELIVERED)
        assert len(next_statuses) == 0


class TestCheckpointData:
    """Tests para el value object CheckpointData"""

    def test_valid_checkpoint_data(self):
        """Test para checkpoint data válido"""
        timestamp = datetime.utcnow()
        checkpoint_data = CheckpointData(
            status=UnitStatus.PICKED_UP,
            timestamp=timestamp,
            location="Centro de distribución",
            notes="Paquete recogido",
        )

        assert checkpoint_data.status == UnitStatus.PICKED_UP
        assert checkpoint_data.timestamp == timestamp
        assert checkpoint_data.location == "Centro de distribución"

    def test_future_timestamp_raises_error(self):
        """Test que timestamp futuro lanza error"""
        future_time = datetime.utcnow() + timedelta(hours=1)

        with pytest.raises(ValueError, match="Timestamp no puede ser futuro"):
            CheckpointData(status=UnitStatus.PICKED_UP, timestamp=future_time)

    def test_long_location_raises_error(self):
        """Test que location muy larga lanza error"""
        long_location = "A" * 201

        with pytest.raises(
            ValueError, match="Location no puede exceder 200 caracteres"
        ):
            CheckpointData(
                status=UnitStatus.PICKED_UP,
                timestamp=datetime.utcnow(),
                location=long_location,
            )


class TestUnit:
    """Tests para la entidad Unit"""

    def test_create_unit(self):
        """Test para crear una unidad"""
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)

        assert unit.tracking_id == tracking_id
        assert unit.current_status == UnitStatus.CREATED
        assert len(unit.checkpoints) == 1
        assert unit.checkpoints[0].status == UnitStatus.CREATED

    def test_add_valid_checkpoint(self):
        """Test para agregar checkpoint válido"""
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)

        checkpoint_data = CheckpointData(
            status=UnitStatus.PICKED_UP, timestamp=datetime.utcnow()
        )

        unit.add_checkpoint(checkpoint_data)

        assert unit.current_status == UnitStatus.PICKED_UP
        assert len(unit.checkpoints) == 2

    def test_add_invalid_checkpoint_raises_error(self):
        """Test que checkpoint inválido lanza error"""
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)

        # Intentar saltar estados
        checkpoint_data = CheckpointData(
            status=UnitStatus.DELIVERED, timestamp=datetime.utcnow()
        )

        with pytest.raises(
            ValueError, match="No se puede cambiar de CREATED a DELIVERED"
        ):
            unit.add_checkpoint(checkpoint_data)

    def test_checkpoint_timestamp_validation(self):
        """Test para validación de timestamp de checkpoint"""
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)

        # Agregar primer checkpoint
        first_checkpoint = CheckpointData(
            status=UnitStatus.PICKED_UP, timestamp=datetime.utcnow()
        )
        unit.add_checkpoint(first_checkpoint)

        # Intentar agregar checkpoint con timestamp anterior
        past_checkpoint = CheckpointData(
            status=UnitStatus.IN_TRANSIT,
            timestamp=datetime.utcnow() - timedelta(hours=1),
        )

        with pytest.raises(
            ValueError,
            match="El timestamp del nuevo checkpoint debe ser posterior al último",
        ):
            unit.add_checkpoint(past_checkpoint)

    def test_unit_is_delivered(self):
        """Test para verificar si unidad está entregada"""
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)

        # Agregar checkpoints hasta DELIVERED (siguiendo las transiciones válidas)
        checkpoints = [
            CheckpointData(status=UnitStatus.PICKED_UP, timestamp=datetime.utcnow()),
            CheckpointData(status=UnitStatus.IN_TRANSIT, timestamp=datetime.utcnow()),
            CheckpointData(
                status=UnitStatus.OUT_FOR_DELIVERY, timestamp=datetime.utcnow()
            ),
            CheckpointData(status=UnitStatus.DELIVERED, timestamp=datetime.utcnow()),
        ]

        for checkpoint in checkpoints:
            unit.add_checkpoint(checkpoint)

        assert unit.is_delivered()
        assert unit.get_delivery_time() is not None


class TestCheckpoint:
    """Tests para la entidad Checkpoint"""

    def test_create_checkpoint(self):
        """Test para crear un checkpoint"""
        tracking_id = TrackingId("TEST123")
        checkpoint_data = CheckpointData(
            status=UnitStatus.PICKED_UP, timestamp=datetime.utcnow()
        )

        checkpoint = Checkpoint.create(tracking_id, checkpoint_data)

        assert checkpoint.tracking_id == tracking_id
        assert checkpoint.checkpoint_data == checkpoint_data
        assert checkpoint.id is not None
