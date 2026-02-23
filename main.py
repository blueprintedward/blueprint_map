"""CLI entry for Blueprint Event System."""

import argparse
import os
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from graph_module import load_blueprint
from overlay_module import (
    draw_point_and_label,
    grid_to_pixel,
    load_blueprint_image,
)
from reasoning_module import get_placement
from search_module import search_event

BLUEPRINT_PATH = os.path.join(os.path.dirname(__file__), "blueprint.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DEFAULT_PDF = os.path.join(os.path.expanduser("~"), "Downloads", "blueprint art05.pdf")


def _blueprint_context(id_to_label: dict) -> str:
    """Build short context string of node ids and labels for LLM."""
    lines = [f"  {nid}: {label}" for nid, label in id_to_label.items()]
    return "\n".join(lines[:80])


def _parse_position(s: str) -> tuple[int, int]:
    """Parse '4,7' -> (4, 7)."""
    parts = s.strip().split(",")
    if len(parts) != 2:
        raise ValueError("Position must be col,row e.g. 4,7")
    return int(parts[0].strip()), int(parts[1].strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Blueprint Event System")
    parser.add_argument("event", nargs="?", help="Event to add to blueprint")
    parser.add_argument("--event", "-e", dest="event_opt", help="Event (alternative)")
    parser.add_argument("--blueprint-pdf", "-b", default=DEFAULT_PDF, help="Path to blueprint PDF")
    parser.add_argument("--position", "-p", help="Override grid position as col,row e.g. 4,7")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash", help="Gemini model name")
    parser.add_argument("--api-key", "-k", help="Google API key (or set GOOGLE_API_KEY)")
    args = parser.parse_args()

    event = args.event or args.event_opt
    if not event:
        parser.error("Provide event as positional arg or --event")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Searching for relevant information...")
    search_summary = search_event(event)

    print("Loading blueprint context...")
    graph, id_to_label = load_blueprint(BLUEPRINT_PATH)
    blueprint_context = _blueprint_context(id_to_label)

    print("Reasoning about placement with Gemini...")
    placement = get_placement(
        event, search_summary, blueprint_context,
        model=args.model,
        api_key=args.api_key,
    )

    if args.position:
        col, row = _parse_position(args.position)
        placement["grid_col"] = col
        placement["grid_row"] = row

    label = placement.get("label", event)
    grid_col = placement.get("grid_col", 0)
    grid_row = placement.get("grid_row", 0)

    print("Loading blueprint PDF and overlaying...")
    base_image = load_blueprint_image(args.blueprint_pdf)
    w, h = base_image.size
    x, y = grid_to_pixel(grid_col, grid_row, w, h, 12, 12)
    draw_point_and_label(base_image, x, y, label)

    img_path = os.path.join(OUTPUT_DIR, f"blueprint_{ts}.png")
    base_image.save(img_path)

    explanation = (
        placement.get("reasoning", "")
        + "\n\n連接節點: " + ", ".join(placement.get("connections", []))
        + f"\n網格座標: ({grid_col}, {grid_row})\n標籤: {label}"
    )
    exp_path = os.path.join(OUTPUT_DIR, f"explanation_{ts}.txt")
    with open(exp_path, "w", encoding="utf-8") as f:
        f.write(f"事件: {event}\n\n")
        f.write(explanation)

    print(f"圖片已儲存: {img_path}")
    print(f"說明已儲存: {exp_path}")
    print(f"\n理由摘要:\n{explanation}")


if __name__ == "__main__":
    main()
