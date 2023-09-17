import json
from pathlib import Path

from bw_hestia_bridge import Converter, set_config

if __name__ == "__main__":
    set_config("use_staging", True)
    c = Converter()

    dirpath = Path(__file__).parent.resolve()
    names = ("bananas", "piggery", "guinea-beef", "oil-palm", "soybean")

    for name in names:
        converted = name + "-converted"
        with open(dirpath / (name + "-converted.json"), "w") as f:
            json.dump(
                c.convert(json.load(open(dirpath / f"{name}.jsonld"))),
                f,
                indent=2,
                ensure_ascii=False,
            )
