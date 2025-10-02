import os
import requests
import webbrowser
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def bannerP70_clickjacking():
    clear_screen()
    console.print(
        Panel(
            "[bold red]🖱️ Clickjacking Vulnerability Checker[/bold red]\n"
            "[white]Mengidentifikasi apakah sebuah situs web dapat di-frame (rentan clickjacking)[/white]",
            title="[bold red]💀 Vulnerability - Clickjacking Scanner[/bold red]",
            box=box.DOUBLE,
            padding=(1, 2),
            border_style="red",
        )
    )

def check_clickjacking_headers(target_url: str) -> dict:
    try:
        response = requests.get(target_url, timeout=10, allow_redirects=True)
        headers = response.headers

        xfo = headers.get("X-Frame-Options", "").strip()
        csp = headers.get("Content-Security-Policy", "").strip()

        return {
            "status_code": response.status_code,
            "X-Frame-Options": xfo if xfo else "-",
            "Content-Security-Policy": csp if csp else "-",
            "is_vulnerable": not xfo and "frame-ancestors" not in csp
        }

    except Exception as e:
        return {
            "error": str(e),
            "is_vulnerable": False
        }

def generate_poc_html(target_url: str, output_file: str):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Clickjacking Test</title>
    <style>
        body {{
            background: #000;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding-top: 100px;
        }}
        iframe {{
            position: absolute;
            top: 50px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            height: 700px;
            opacity: 0.1;
            z-index: 10;
            border: none;
        }}
        .cover {{
            z-index: 20;
            position: relative;
        }}
        .cover button {{
            padding: 15px 30px;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <h1>Clickjacking Test</h1>
    <p class="cover">Klik tombol ini tapi yang terjadi tidak seperti yang kamu harapkan 😈</p>
    <button class="cover">Klik Saya!</button>
    <iframe src="{target_url}"></iframe>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    return output_file

def start_clickjacking_scan():
    bannerP70_clickjacking()

    target_url = Prompt.ask("🌐 Masukkan URL target", default="https://example.com").strip()
    if not target_url.startswith("http"):
        console.print("[red]❌ URL tidak valid. Harus diawali dengan http:// atau https://[/red]")
        return

    console.print(f"[cyan]🔍 Mengecek header proteksi clickjacking pada: [bold]{target_url}[/bold][/cyan]")
    result = check_clickjacking_headers(target_url)

    if "error" in result:
        console.print(f"[red]❌ Gagal mengakses URL: {result['error']}[/red]")
        return

    # Tampilkan hasil
    table = Table(title="📋 Hasil Analisis Header", box=box.SIMPLE_HEAVY)
    table.add_column("Header", style="cyan", no_wrap=True)
    table.add_column("Nilai", style="white")

    table.add_row("Status Kode", str(result["status_code"]))
    table.add_row("X-Frame-Options", result["X-Frame-Options"])
    table.add_row("Content-Security-Policy", result["Content-Security-Policy"])
    table.add_row("Rentan Clickjacking?", "[bold green]Ya[/bold green]" if result["is_vulnerable"] else "[bold red]Tidak[/bold red]")

    console.print(table)

    # Jika rentan, buat file HTML
    if result["is_vulnerable"]:
        parsed = urlparse(target_url)
        domain_name = parsed.netloc.replace(".", "_")
        file_name = f"clickjacking_{domain_name}.html"
        path = os.path.abspath(generate_poc_html(target_url, file_name))
        console.print(f"\n[green]✅ Target rentan! File PoC HTML disimpan di:[/green] [bold]{path}[/bold]")

        open_choice = Prompt.ask("🚀 Ingin membuka file PoC di browser?", choices=["y", "n"], default="y")
        if open_choice == "y":
            webbrowser.open(f"file://{path}")
    else:
        console.print("\n[bold yellow]🚫 Target memiliki proteksi terhadap iframe. Tidak rentan terhadap clickjacking.[/bold yellow]")

    console.input("\n[bold cyan]Tekan Enter untuk kembali ke submenu...[/bold cyan]")

def clickjacking_menu():
    start_clickjacking_scan()


clickjacking_menu()
