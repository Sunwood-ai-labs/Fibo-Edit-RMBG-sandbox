# Troubleshooting

## Hugging Face token errors

If the CLI reports that `HF_TOKEN` is missing:

- copy `.env.example` to `.env`
- set `HF_TOKEN`
- confirm your account has accepted the gated model access request

## Memory pressure on 6GB GPUs

The saved experiments were run on an RTX 3060 6GB setup. The main practical findings were:

- `max-side 256` is the safest stable starting point
- `balanced / 320 / 4 steps` can fail on heavier inputs
- `hard` does not solve memory pressure; it mainly changes edge post-processing behavior

## CPU offload caveat

`--cpu-offload` was not reliable on the tested Windows setup because the stack hit backend/kernel failures during decoding. Treat it as experimental in this repository.

## Pages and docs

To build the docs locally:

```powershell
Set-Location .\docs
npm install
npm run docs:build
```
