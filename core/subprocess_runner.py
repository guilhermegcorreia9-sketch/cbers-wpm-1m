# -*- coding: utf-8 -*-
# Created by Miguel Alexandre da Cunha; Guilherme Gomes Correia
import sys
import os
import json
import signal
import traceback

_CANCEL_REQUESTED = False

def _install_signal_handlers():
    def _handle(signum, frame):
        global _CANCEL_REQUESTED
        _CANCEL_REQUESTED = True

    for sig_name in ("SIGTERM", "SIGINT", "SIGBREAK"):
        sig = getattr(signal, sig_name, None)
        if sig is None:
            continue
        try:
            signal.signal(sig, _handle)
        except (ValueError, OSError):
            pass

def main():
    if len(sys.argv) != 4:
        print("ERROR: uso: subprocess_runner.py <mode> <params_json_path> <result_json_path>", flush=True)
        sys.exit(2)

    mode, params_path, result_path = sys.argv[1], sys.argv[2], sys.argv[3]

    plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)

    from core.pipeline import run_pipeline, search_available_scenes, PipelineError, PipelineCancelled

    with open(params_path, "r", encoding="utf-8") as f:
        params = json.load(f)

    def log(*args):
        msg = "LOG: " + " ".join(str(a) for a in args)
        try:
            print(msg, flush=True)
        except UnicodeEncodeError:
            enc = getattr(sys.stdout, "encoding", None) or "utf-8"
            safe = msg.encode(enc, errors="replace").decode(enc, errors="replace")
            print(safe, flush=True)

    def should_cancel():
        return _CANCEL_REQUESTED

    _install_signal_handlers()

    result = {"ok": False, "outputs": [], "results": [], "error": None}
    try:
        if mode == "process":
            outputs = run_pipeline(params, log=log, should_cancel=should_cancel)
            result["ok"] = True
            result["outputs"] = outputs
        elif mode == "search":
            results = search_available_scenes(params, log=log)
            result["ok"] = True
            result["results"] = results
        else:
            raise ValueError("Modo desconhecido: {}".format(mode))
    except (PipelineError, PipelineCancelled) as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = "Erro inesperado: {}\n\n{}".format(exc, traceback.format_exc())

    tmp_path = result_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    os.replace(tmp_path, result_path)

    sys.exit(0 if result["ok"] else 1)

if __name__ == "__main__":
    main()
