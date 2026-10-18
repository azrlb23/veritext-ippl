#!/usr/bin/env python3
"""
render_diagram.py - Automated Flowchart & Diagram to PNG/SVG Renderer
Part of the flowchart-maker skill for Google Antigravity.
Uses the Kroki API (Zlib level 9 + Base64 URL-safe encoding) to convert
Mermaid, PlantUML, Graphviz, and D2 diagrams directly into high-resolution PNGs.
"""

import argparse
import base64
import os
import sys
import urllib.error
import urllib.request
import zlib

def encode_diagram(source_code: str) -> str:
    """Encodes diagram source code using zlib compression and URL-safe base64."""
    data = source_code.strip().encode("utf-8")
    compressed = zlib.compress(data, 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").replace("=", "")
    return encoded

def get_kroki_url(source_code: str, diagram_type: str = "mermaid", output_format: str = "png") -> str:
    """Returns the Kroki API endpoint URL for the diagram."""
    encoded = encode_diagram(source_code)
    return f"https://kroki.io/{diagram_type}/{output_format}/{encoded}"

def render_diagram(source_code: str, output_path: str, diagram_type: str = "mermaid", output_format: str = "png") -> bool:
    """
    Renders diagram code to a local image file.
    Returns True if downloaded successfully, False otherwise.
    """
    url = get_kroki_url(source_code, diagram_type, output_format)
    print(f"[*] Diagram Kroki URL: {url}")
    
    # Ensure parent directory exists
    parent_dir = os.path.dirname(os.path.abspath(output_path))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
        
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AntigravityFlowchartMaker/1.0"}
    )
    
    try:
        print(f"[*] Downloading {output_format.upper()} image to: {output_path}...")
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                content = response.read()
                with open(output_path, "wb") as f:
                    f.write(content)
                size_kb = len(content) / 1024
                print(f"[✓] Berhasil! Berkas gambar tersimpan: {output_path} ({size_kb:.2f} KB)")
                return True
            else:
                print(f"[!] Server mengembalikan status: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"[!] HTTP Error {e.code}: {e.reason}")
        try:
            err_msg = e.read().decode('utf-8', errors='ignore')
            print(f"[!] Pesan galat dari Kroki:\n{err_msg}")
        except Exception:
            pass
        return False
    except urllib.error.URLError as e:
        print(f"[!] Koneksi gagal (Offline/Sandbox): {e.reason}")
        print(f"[*] Tautan langsung gambar PNG: {url}")
        return False
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Render diagram code to PNG/SVG via Kroki")
    parser.add_argument("input_file", nargs="?", help="Path to input diagram file (.mmd, .puml, .dot)")
    parser.add_argument("-c", "--code", help="Inline diagram code string")
    parser.add_argument("-o", "--output", required=True, help="Target output image path (e.g., output.png)")
    parser.add_argument("-t", "--type", default="mermaid", choices=["mermaid", "plantuml", "graphviz", "d2", "bpmn", "c4plantuml"], help="Diagram engine type (default: mermaid)")
    parser.add_argument("-f", "--format", default="png", choices=["png", "svg", "jpeg", "pdf"], help="Output image format (default: png)")
    
    args = parser.parse_args()
    
    if args.code:
        source_code = args.code
    elif args.input_file:
        if not os.path.exists(args.input_file):
            print(f"[!] Berkas masukan tidak ditemukan: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    else:
        print("[!] Harap sertakan berkas masukan atau opsi --code", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
        
    success = render_diagram(
        source_code=source_code,
        output_path=args.output,
        diagram_type=args.type,
        output_format=args.format
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
