import logging
import re
import orjson
from pathlib import Path

logger = logging.getLogger(__name__)
PROJECT_DIR_PATH = Path(__file__).parent


def update_coordinates() -> None:
    skipped_airports = {}
    for place_id, inconsistency in orjson.loads((PROJECT_DIR_PATH / "airports.json").read_bytes()).items():
        if "expected coordinates" in inconsistency:
            coordinates = re.findall("\(\-?\d+\.\d+,\s\-?\d+\.\d+\)", inconsistency)[0][1:-1].split(", ")
            path = ""
            _place_id = place_id
            while _place_id:
                path = _place_id[:3] if not path else f"{path}/{_place_id[:3]}"
                _place_id = _place_id[3:]
            if (file_path := (PROJECT_DIR_PATH / "data" / path / f"{place_id}.geojson")).is_file():
                logger.info(f"Updating place with place_id: {place_id}.")
                geojson_data = orjson.loads(file_path.read_bytes())
                geojson_data["properties"]["geom:latitude"] = float(coordinates[1])
                geojson_data["properties"]["geom:longitude"] = float(coordinates[0])
                file_path.write_bytes(orjson.dumps(geojson_data))
            else:
                logger.warning(f"Skipping place with place_id: {place_id}.")
                skipped_airports.update({place_id: inconsistency})
    (PROJECT_DIR_PATH / "skipped_airports.json").write_bytes(orjson.dumps(skipped_airports))


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(levelname)-7s %(funcName)s: %(message)s")
    update_coordinates()