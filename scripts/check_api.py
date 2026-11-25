import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def call(path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(BASE_URL + path, data, {"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def main():
    for _ in range(30):
        try:
            if call("/health") == (200, b'{"status":"ok"}'):
                break
        except URLError:
            pass
        time.sleep(1)
    else:
        raise SystemExit("API did not start")

    status, docs = call("/docs")
    assert status == 200 and b"Swagger UI" in docs
    assert "/predict" in json.loads(call("/openapi.json")[1])["paths"]

    trip = {
        "vendor_id": 1,
        "passenger_count": 2,
        "pickup_longitude": -74.0064,
        "pickup_latitude": 40.7337,
        "pickup_hour": 20,
        "pickup_weekday": 5,
    }
    status, body = call("/predict", trip)
    prediction = json.loads(body)
    assert status == 200
    assert prediction["predicted_class"] == 0
    assert 0 <= prediction["long_trip_probability"] < 0.5
    print(f"/predict: {status} {prediction}", flush=True)

    for invalid, field in [
        ({**trip, "pickup_hour": 24}, "pickup_hour"),
        ({**trip, "passenger_count": "2"}, "passenger_count"),
        ({**trip, "vendor_id": True}, "vendor_id"),
        ({**trip, "trip_duration": 1000}, "trip_duration"),
        ({key: value for key, value in trip.items() if key != "pickup_latitude"},
         "pickup_latitude"),
    ]:
        status, body = call("/predict", invalid)
        assert status == 422, body
        assert any(err["loc"][-1] == field for err in json.loads(body)["detail"])
        print(f"Invalid {field}: {status}", flush=True)


if __name__ == "__main__":
    main()
