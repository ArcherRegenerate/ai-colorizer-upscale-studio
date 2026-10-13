# Contributing to ai-colorizer-upscale-studio

Thanks for wanting to help. This repo is the desktop GUI + CLI for AI
coloring and upscaling of images. It wraps ONNX Runtime (CPU/CUDA) and,
optionally, TensorRT engines for the heavier super-resolution models.

## Dev setup

```bash
git clone https://github.com/yourname/ai-colorizer-upscale-studio
cd ai-colorizer-upscale-studio
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

Models are downloaded on first run into `models/weights/` unless you
drop `.onnx` files there manually. See `models/weights/README` (created
on first bootstrap) for the expected filenames.

## Architecture

Service-oriented. Thin handlers (`app/handlers/`) receive GUI/CLI events
and immediately delegate to services (`app/services/`). Services own the
actual work — colorization, upscaling, batch orchestration, model
resolution. Models (`app/models/`) are pydantic schemas for jobs,
results, and config. Platform adapters (`app/adapters/`) isolate
ONNX Runtime, TensorRT, and the filesystem.

## Style

- `ruff` + `black`, line length 100.
- `mypy --strict` on `app/`.
- No business logic in handlers. If a handler is longer than ~40 lines,
  it belongs in a service.
- Every service method has a docstring with inputs, outputs, error modes.

## Submitting

1. Fork, branch from `main`: `feat/<short-name>` or `fix/<short-name>`.
2. Run `ruff check app tests && mypy app && pytest`.
3. Open a PR. Include a sample image pair (before/after) if it touches
   the colorizer or upscaler pipelines.

## Reporting model issues

If a specific model produces banding, color bleed, or hallucinated
detail, open an issue with the model name, input resolution, and the
exact CLI invocation. Attach the input image if you can share it.