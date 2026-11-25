import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from unittest.mock import Mock

import pytest


def load_gpio_module() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "olaf" / "board" / "gpio.py"
    spec = spec_from_file_location("gpio_under_test", path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def gpio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> ModuleType:
    module = load_gpio_module()
    monkeypatch.setattr(module.Gpio, "_GPIO_DIR_PATH", str(tmp_path))
    labelled = tmp_path / "gpio7"
    labelled.mkdir()
    (labelled / "label").write_text("LED\n")
    (labelled / "direction").write_text("out")
    (labelled / "value").write_text("0")
    (tmp_path / "gpio8").mkdir()
    (tmp_path / "gpiochip512").mkdir()
    (tmp_path / "export").touch()
    (tmp_path / "unexport").touch()
    return module


def test_import_with_unlabelled_gpio(monkeypatch: pytest.MonkeyPatch) -> None:
    with monkeypatch.context() as patch:
        patch.setattr("os.path.isdir", Mock(return_value=True))
        patch.setattr("os.listdir", Mock(return_value=["gpio595"]))
        patch.setattr("builtins.open", Mock(side_effect=FileNotFoundError("gpio595/label")))
        module = load_gpio_module()
        pin = module.Gpio("MOCK_PIN", mock=True)
        pin.high()
        assert pin.is_high
        pin.low()
        assert not pin.is_high


def test_named_gpio_skips_unlabelled_pins(gpio: ModuleType, tmp_path: Path) -> None:
    pin = gpio.Gpio("LED")
    assert pin.number == 7
    assert pin.name.strip() == "LED"
    pin.high()
    assert (tmp_path / "gpio7" / "value").read_text() == "1"
    pin.low()
    assert (tmp_path / "gpio7" / "value").read_text() == "0"


def test_mock_gpio_does_not_scan(gpio: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("os.listdir", Mock(side_effect=AssertionError("unexpected GPIO scan")))
    pin = gpio.Gpio("UNAVAILABLE", mock=True)
    pin.high()
    assert pin.value == gpio.GPIO_HIGH
    pin.mode = gpio.GPIO_IN
    with pytest.raises(gpio.GpioError, match="input mode"):
        pin.low()


def test_numeric_gpio_does_not_scan(gpio: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("os.listdir", Mock(side_effect=AssertionError("unexpected GPIO scan")))
    pin = gpio.Gpio(7)
    assert pin.number == 7
    assert pin.value == gpio.GPIO_LOW


def test_unknown_gpio_label(gpio: ModuleType) -> None:
    with pytest.raises(KeyError, match="UNKNOWN"):
        gpio.Gpio("UNKNOWN")


def test_gpio_label_permission_error(gpio: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.open", Mock(side_effect=PermissionError("GPIO label")))
    with pytest.raises(PermissionError, match="GPIO label"):
        gpio.Gpio("LED")


@pytest.mark.skipif(sys.platform != "linux", reason="OLAF package imports require Linux")
def test_oresat_file_import_with_unlabelled_gpio() -> None:
    script = dedent(
        """
        import builtins
        import os
        from unittest.mock import patch

        root = "/sys/class/gpio"
        real_isdir = os.path.isdir
        real_listdir = os.listdir
        real_open = builtins.open

        def isdir(path):
            return True if path == root else real_isdir(path)

        def listdir(path):
            if path == root:
                return ["gpiochip512", "export", "unexport", "gpio595"]
            return real_listdir(path)

        def open_file(path, *args, **kwargs):
            if str(path).startswith(root + "/"):
                raise FileNotFoundError(str(path))
            return real_open(path, *args, **kwargs)

        with patch("os.path.isdir", side_effect=isdir), \
             patch("os.listdir", side_effect=listdir), \
             patch("builtins.open", side_effect=open_file):
            from olaf import OreSatFile
            assert OreSatFile("name_test_12345.txt").name == "name_test_12345.txt"
        """
    )
    subprocess.run(  # noqa: S603 - fixed interpreter and regression script
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
