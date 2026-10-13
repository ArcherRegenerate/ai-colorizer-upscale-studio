# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.9.x   | Yes       |
| 0.8.x   | Critical fixes only |
| < 0.8   | No        |

## Reporting a vulnerability

Email `security@colorizer-upscale.studio` (PGP key on the repo wiki).
Do not open a public issue for memory-safety bugs, path traversal in
the batch importer, or anything that could let a malicious `.onnx`
model execute arbitrary code via custom ops.

## Threat model

This tool loads third-party model files (`.onnx`, `.trt`, `.engine`).
ONNX custom operators and TensorRT plugins are executed in-process. Do
not load models from untrusted sources. The bundled loader validates
the ONNX magic bytes and op-set version but does not sandbox custom ops.

## Out of scope

- Denial of service via giant images (documented, not treated as a vuln).
- GPU driver crashes caused by bad TensorRT engines.
- Local privilege escalation that requires an already-compromised host.

## Disclosure

We aim to acknowledge within 72 hours and ship a fix or mitigation
within 14 days for high-severity issues.