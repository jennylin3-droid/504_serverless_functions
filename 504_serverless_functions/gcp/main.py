import json
import logging
import functions_framework

# Configure basic logging so stack traces and messages appear in Cloud Run logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def hba1c_classifier(request):
    """HTTP Cloud Function.
    Expects JSON with 'hba1c' (or query param as fallback).
    Returns a JSON classification of glycemic status.
    """
    try:
        # Prefer JSON body; fall back to query parameters for convenience
        data = request.get_json(silent=True) or {}
        args = request.args or {}

        hba1c = data.get("hba1c", args.get("hba1c"))

        # Presence check
        if hba1c is None:
            return (
                json.dumps({"error": "Field 'hba1c' is required."}),
                400,
                {"Content-Type": "application/json"},
            )

        # Type/convert check
        try:
            hba1c_val = float(hba1c)
        except (TypeError, ValueError):
            return (
                json.dumps({"error": "'hba1c' must be a number."}),
                400,
                {"Content-Type": "application/json"},
            )

        # Classification logic (ADA 2024)
        if hba1c_val < 5.7:
            status = "normal"
            category = "Normal (<5.7%)"
        elif 5.7 <= hba1c_val < 6.5:
            status = "prediabetes"
            category = "Prediabetes (5.7\u20136.4%)"
        else:
            status = "diabetes"
            category = "Diabetes (\u22656.5%)"

        payload = {
            "hba1c": hba1c_val,
            "status": status,
            "category": category,
        }

        return json.dumps(payload), 200, {"Content-Type": "application/json"}

    except Exception as e:
        # Log full exception with stack trace — visible in Cloud Run logs
        logger.exception("Unhandled exception in hba1c_classifier")

        # Return a concise JSON error to the caller
        err_payload = {"error": "internal_server_error", "message": str(e)}
        return json.dumps(err_payload), 500, {"Content-Type": "application/json"}
