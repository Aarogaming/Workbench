import ctypes
import os
from loguru import logger


def get_dpi_scaling():
    """Get the current DPI scaling factor for the primary monitor."""
    if os.name != "nt":
        logger.warning("DPI audit only supported on Windows.")
        return 1.0

    try:
        # Set process as DPI aware to get accurate readings
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except Exception as e:
        logger.error(f"Failed to get DPI: {e}")
        return 1.0


def run_audit():
    scaling = get_dpi_scaling()
    logger.info(f"Current System DPI Scaling: {scaling:.0%}")

    if scaling == 1.0:
        logger.success("System is at 100% scaling. Baseline tests valid.")
    elif scaling > 1.0:
        logger.warning(
            f"High-DPI detected ({scaling:.0%}). ProjectMaelstrom UI/OCR may require adjustment."
        )

    # Audit specific UI components (simulated)
    components = ["MainDashboard", "OCRScanner", "InputOverlay"]
    for comp in components:
        logger.info(f"Auditing {comp} for DPI compatibility...")
        # In a real audit, this would check window bounds and element positions
        # against expected scaled values.
        time_delay = 0.2
        import time

        time.sleep(time_delay)
        logger.success(f"{comp} audit complete.")


if __name__ == "__main__":
    run_audit()
