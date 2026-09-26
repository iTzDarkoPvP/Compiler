#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import threading
import time
import os
import json
import subprocess
import shutil
import zipfile
import tempfile
import platform
import sys

INICIO_PUERTO = 1000
MAX_PUERTO = 65535


def detectar_sistema():
    if os.environ.get('TERMUX_VERSION') or shutil.which('termux-open-url') or 'com.termux' in os.environ.get('PREFIX', ''):
        return 'termux'
    sistema = platform.system()
    if sistema == 'Windows':
        return 'windows'
    if sistema == 'Darwin':
        return 'mac'
    return 'linux'


def verificar_dependencias():
    print("🔍 Verificando dependencias...")
    dependencias = {
        'javac': 'openjdk-17-jdk',
        'jar': 'openjdk-17-jdk',
        'python3': 'python3',
        'pip': 'python3-pip'
    }
    dependencias_faltan = []
    for cmd, pkg in dependencias.items():
        if shutil.which(cmd) is None:
            dependencias_faltan.append(pkg)

    if not dependencias_faltan:
        print("✅ Dependencias verificadas")
        return True

    sistema = detectar_sistema()

    if sistema == 'windows':
        print("📦 Faltan dependencias. En Windows instálalas manualmente:")
        for pkg in dependencias_faltan:
            print(f"   - {pkg} (instala el JDK desde https://adoptium.net y agrega javac/jar al PATH)")
        return False

    print("📦 Instalando dependencias faltantes...")
    try:
        if shutil.which('apt'):
            for pkg in dependencias_faltan:
                os.system(f'sudo apt-get install -y {pkg}')
        elif shutil.which('pkg'):
            for pkg in dependencias_faltan:
                os.system(f'pkg install -y {pkg}')
        elif shutil.which('pacman'):
            for pkg in dependencias_faltan:
                os.system(f'sudo pacman -S --noconfirm {pkg}')
        elif shutil.which('brew'):
            for pkg in dependencias_faltan:
                os.system(f'brew install {pkg}')
        else:
            print("⚠️ No se pudo detectar el gestor de paquetes. Instala manualmente:")
            for pkg in dependencias_faltan:
                print(f"   - {pkg}")
            return False
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

    print("✅ Dependencias verificadas")
    return True


def verificar_nukkit_jar():
    nukkit_jar = 'nukkit.jar'
    if os.path.exists(nukkit_jar):
        print(f"✅ nukkit.jar encontrado")
        return True
    print("⚠️ No se encontró nukkit.jar")
    print("   Coloca el archivo nukkit.jar en esta misma carpeta para poder compilar")
    if os.path.exists('server.jar'):
        print("   📦 Se encontró server.jar, renombrando a nukkit.jar...")
        try:
            shutil.move('server.jar', 'nukkit.jar')
            print("✅ nukkit.jar creado desde server.jar")
            return True
        except Exception as e:
            print(f"❌ Error renombrando: {e}")
    respuesta = input("   ¿Deseas descargar nukkit.jar automáticamente? (s/n): ")
    if respuesta.lower() == 's':
        print("   📥 Descargando nukkit.jar...")
        try:
            import urllib.request
            url = "https://ci.opencollab.dev/job/Nukkit/job/Nukkit/job/master/lastSuccessfulBuild/artifact/target/nukkit-1.0-SNAPSHOT.jar"
            urllib.request.urlretrieve(url, 'nukkit.jar')
            print("   ✅ nukkit.jar descargado correctamente")
            return True
        except Exception as e:
            print(f"   ❌ Error descargando: {e}")
            print("   Descarga manual desde: https://ci.opencollab.dev/job/Nukkit/job/Nukkit/job/master/")
    return False


HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Nukkit Compiler Pro</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');

        :root {
            --bg-primary: #f5f5f5;
            --bg-secondary: #ffffff;
            --bg-panel: #fafafa;
            --bg-input: #f5f5f5;
            --bg-console: #f8f8f8;
            --border-color: #eeeeee;
            --border-hover: #cccccc;
            --text-primary: #000000;
            --text-secondary: #333333;
            --text-muted: #888888;
            --text-light: #aaaaaa;
            --text-lighter: #bbbbbb;
            --shadow: 0 20px 60px rgba(0,0,0,0.06);
            --shadow-hover: 0 12px 40px rgba(0,0,0,0.04);
            --btn-primary: #000000;
            --btn-primary-hover: #222222;
            --btn-success: #333333;
            --btn-success-hover: #444444;
            --btn-danger: #f5f5f5;
            --btn-danger-hover: #eeeeee;
            --badge-bg: #f0f0f0;
            --badge-text: #aaaaaa;
            --drop-border: #dddddd;
            --drop-hover: #999999;
            --drop-bg: #fafafa;
            --file-item-hover: #f5f5f5;
            --scroll-track: #f5f5f5;
            --scroll-thumb: #dddddd;
            --gradient-start: #000000;
            --gradient-end: #555555;
            --divider-color: #000000;
            --divider-opacity: 0.15;
            --footer-border: #eeeeee;
            --footer-text: #cccccc;
            --dot-bg: #dddddd;
            --log-info: #888888;
            --log-success: #000000;
            --log-error: #cc0000;
            --log-warning: #cc8800;
            --log-system: #bbbbbb;
            --transition: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        [data-theme="dark"] {
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-panel: #141414;
            --bg-input: #1a1a1a;
            --bg-console: #0d0d0d;
            --border-color: #2a2a2a;
            --border-hover: #444444;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --text-muted: #888888;
            --text-light: #666666;
            --text-lighter: #555555;
            --shadow: 0 20px 60px rgba(0,0,0,0.4);
            --shadow-hover: 0 12px 40px rgba(0,0,0,0.3);
            --btn-primary: #ffffff;
            --btn-primary-hover: #dddddd;
            --btn-success: #444444;
            --btn-success-hover: #555555;
            --btn-danger: #222222;
            --btn-danger-hover: #333333;
            --badge-bg: #2a2a2a;
            --badge-text: #666666;
            --drop-border: #333333;
            --drop-hover: #666666;
            --drop-bg: #111111;
            --file-item-hover: #1a1a1a;
            --scroll-track: #1a1a1a;
            --scroll-thumb: #333333;
            --gradient-start: #ffffff;
            --gradient-end: #888888;
            --divider-color: #ffffff;
            --divider-opacity: 0.2;
            --footer-border: #2a2a2a;
            --footer-text: #444444;
            --dot-bg: #333333;
            --log-info: #666666;
            --log-success: #ffffff;
            --log-error: #ff4444;
            --log-warning: #ffaa44;
            --log-system: #444444;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color var(--transition), color var(--transition), border-color var(--transition), box-shadow var(--transition);
        }

        body {
            width: 100vw;
            min-height: 100vh;
            overflow-x: hidden;
            background: var(--bg-primary);
            display: flex;
            justify-content: center;
            align-items: flex-start;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            padding: 20px;
            position: relative;
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 22px;
            box-shadow: var(--shadow);
            transition: all var(--transition);
            user-select: none;
        }

        .theme-toggle:hover {
            transform: scale(1.05) rotate(15deg);
            border-color: var(--border-hover);
            box-shadow: var(--shadow-hover);
        }

        .bg-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background:
                radial-gradient(ellipse at 20% 50%, rgba(0,0,0,0.03) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(0,0,0,0.03) 0%, transparent 60%);
        }

        [data-theme="dark"] .bg-pattern {
            background:
                radial-gradient(ellipse at 20% 50%, rgba(255,255,255,0.03) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(255,255,255,0.03) 0%, transparent 60%);
        }

        .bg-pattern .grid {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                linear-gradient(var(--border-color) 1px, transparent 1px),
                linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
            background-size: 60px 60px;
            opacity: 0.4;
        }

        [data-theme="dark"] .bg-pattern .grid {
            opacity: 0.15;
        }

        .container {
            width: 100%;
            max-width: 1200px;
            padding: 40px 40px 30px;
            background: var(--bg-secondary);
            border-radius: 28px;
            position: relative;
            z-index: 1;
            opacity: 0;
            transform: translateY(30px) scale(0.97);
            animation: containerIn 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
            box-shadow: var(--shadow);
        }

        @keyframes containerIn {
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .header {
            text-align: center;
            margin-bottom: 35px;
            opacity: 0;
            transform: translateY(-15px);
            animation: slideDown 0.7s ease-out 0.4s forwards;
        }

        @keyframes slideDown {
            to { opacity: 1; transform: translateY(0); }
        }

        .header .logo-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin-bottom: 4px;
        }

        .header .logo-icon {
            font-size: 36px;
            animation: iconPulse 3s ease-in-out infinite;
        }

        @keyframes iconPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .header h1 {
            font-size: 32px;
            font-weight: 100;
            letter-spacing: 8px;
            text-transform: uppercase;
            color: var(--text-primary);
        }

        .header h1 .highlight {
            font-weight: 900;
            background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 50%, var(--gradient-start) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200% 200%;
            animation: shineText 4s ease-in-out infinite;
        }

        @keyframes shineText {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .header .subtitle {
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 400;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 2px;
        }

        .header .divider {
            width: 60px;
            height: 2px;
            margin: 14px auto 0;
            background: var(--divider-color);
            opacity: var(--divider-opacity);
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }

        .panel {
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 26px 26px 30px;
            transition: all var(--transition);
            opacity: 0;
            transform: translateY(20px);
            animation: panelIn 0.7s ease-out forwards;
        }

        .panel:nth-of-type(1) { animation-delay: 0.5s; }
        .panel:nth-of-type(2) { animation-delay: 0.6s; }

        @keyframes panelIn {
            to { opacity: 1; transform: translateY(0); }
        }

        .panel:hover {
            border-color: var(--border-hover);
            transform: translateY(-3px);
            box-shadow: var(--shadow-hover);
        }

        .panel-title {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-light);
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .panel-title .badge {
            background: var(--badge-bg);
            padding: 2px 12px;
            border-radius: 50px;
            font-size: 8px;
            color: var(--badge-text);
            letter-spacing: 1.5px;
        }

        .panel-title .icon-title {
            font-size: 16px;
        }

        .drop-zone {
            border: 2px dashed var(--drop-border);
            border-radius: 14px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all var(--transition);
            background: var(--drop-bg);
        }

        .drop-zone:hover {
            border-color: var(--drop-hover);
            background: var(--bg-input);
        }

        .drop-zone.dragover {
            border-color: var(--text-primary);
            background: var(--bg-panel);
            box-shadow: 0 0 40px rgba(0,0,0,0.04);
        }

        [data-theme="dark"] .drop-zone.dragover {
            box-shadow: 0 0 40px rgba(255,255,255,0.03);
        }

        .drop-zone .icon-drop {
            font-size: 44px;
            display: block;
            margin-bottom: 12px;
            opacity: 0.4;
            transition: all var(--transition);
        }

        .drop-zone:hover .icon-drop {
            opacity: 0.7;
            transform: scale(1.05);
        }

        .drop-zone p {
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 400;
            letter-spacing: 0.3px;
        }

        .drop-zone p strong {
            color: var(--text-secondary);
            font-weight: 600;
        }

        .drop-zone .sub-text {
            color: var(--text-light);
            font-size: 12px;
            margin-top: 6px;
            letter-spacing: 1px;
        }

        .drop-zone input[type="file"] {
            display: none;
        }

        .file-info {
            margin-top: 14px;
            padding: 12px 18px;
            background: var(--bg-input);
            border-radius: 10px;
            border: 1px solid var(--border-color);
            display: none;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            animation: fadeSlide 0.4s ease;
        }

        @keyframes fadeSlide {
            from { opacity: 0; transform: translateY(-8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .file-info .name {
            color: var(--text-primary);
            font-weight: 500;
            font-size: 14px;
        }

        .file-info .size {
            color: var(--text-light);
            font-size: 12px;
        }

        .file-info .status-badge {
            padding: 3px 14px;
            border-radius: 50px;
            background: var(--badge-bg);
            color: var(--text-muted);
            font-size: 9px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        .file-info .status-badge.loaded {
            background: var(--btn-primary);
            color: var(--bg-secondary);
        }

        [data-theme="dark"] .file-info .status-badge.loaded {
            background: var(--btn-primary);
            color: var(--bg-secondary);
        }

        .plugin-name-display {
            margin-top: 12px;
            padding: 10px 16px;
            background: var(--bg-input);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            display: none;
            align-items: center;
            gap: 12px;
            animation: fadeSlide 0.4s ease;
        }

        .plugin-name-display .label {
            color: var(--text-light);
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .plugin-name-display .value {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 14px;
        }

        .file-list {
            margin-top: 12px;
            max-height: 150px;
            overflow-y: auto;
        }

        .file-list::-webkit-scrollbar {
            width: 4px;
        }

        .file-list::-webkit-scrollbar-track {
            background: var(--scroll-track);
            border-radius: 2px;
        }

        .file-list::-webkit-scrollbar-thumb {
            background: var(--scroll-thumb);
            border-radius: 2px;
        }

        .file-item {
            display: flex;
            justify-content: space-between;
            padding: 6px 10px;
            border-bottom: 1px solid var(--border-color);
            font-size: 12px;
            color: var(--text-muted);
            transition: all var(--transition);
            font-family: 'Inter', monospace;
        }

        .file-item:hover {
            background: var(--file-item-hover);
            color: var(--text-secondary);
            padding-left: 14px;
        }

        .file-item .size {
            color: var(--text-light);
            font-size: 10px;
        }

        .file-item .type {
            color: var(--text-lighter);
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-left: 10px;
        }

        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        .btn {
            padding: 10px 26px;
            border: none;
            border-radius: 10px;
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all var(--transition);
            position: relative;
            overflow: hidden;
            flex: 1;
            min-width: 80px;
            text-align: center;
        }

        .btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(0,0,0,0.04);
            transition: all 0.6s ease;
            transform: translate(-50%, -50%);
        }

        [data-theme="dark"] .btn::after {
            background: rgba(255,255,255,0.04);
        }

        .btn:active::after {
            width: 400px;
            height: 400px;
        }

        .btn-primary {
            color: var(--bg-secondary);
            background: var(--btn-primary);
        }

        .btn-primary:hover {
            background: var(--btn-primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }

        .btn-success {
            color: var(--bg-secondary);
            background: var(--btn-success);
        }

        .btn-success:hover {
            background: var(--btn-success-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }

        .btn-danger {
            color: var(--text-muted);
            background: var(--btn-danger);
            border: 1px solid var(--border-color);
        }

        .btn-danger:hover {
            color: var(--text-secondary);
            background: var(--btn-danger-hover);
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 14px 0;
        }

        .stat-card {
            background: var(--bg-input);
            padding: 14px 10px;
            text-align: center;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            transition: all var(--transition);
        }

        .stat-card:hover {
            background: var(--bg-panel);
            border-color: var(--border-hover);
        }

        .stat-card .value {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: 0.5px;
            font-variant-numeric: tabular-nums;
        }

        .stat-card .label {
            font-size: 9px;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 4px;
        }

        .jar-name-display {
            margin: 12px 0 14px;
            padding: 10px 16px;
            background: var(--bg-input);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .jar-name-display .label {
            color: var(--text-light);
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .jar-name-display .name {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 14px;
        }

        .progress-container {
            margin: 14px 0 0;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 2px;
            background: var(--border-color);
            border-radius: 2px;
            overflow: hidden;
        }

        .progress-bar .fill {
            height: 100%;
            background: var(--text-primary);
            width: 0%;
            transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            border-radius: 2px;
        }

        .progress-text {
            font-size: 9px;
            color: var(--text-light);
            letter-spacing: 1.5px;
            margin-top: 6px;
            text-align: right;
            font-variant-numeric: tabular-nums;
        }

        .console {
            background: var(--bg-console);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px 18px;
            min-height: 120px;
            max-height: 180px;
            overflow-y: auto;
            font-family: 'Inter', 'Courier New', monospace;
            font-size: 11px;
            line-height: 2.2;
        }

        .console::-webkit-scrollbar {
            width: 4px;
        }

        .console::-webkit-scrollbar-track {
            background: var(--scroll-track);
            border-radius: 2px;
        }

        .console::-webkit-scrollbar-thumb {
            background: var(--scroll-thumb);
            border-radius: 2px;
        }

        .console .log-info { color: var(--log-info); }
        .console .log-success { color: var(--log-success); }
        .console .log-error { color: var(--log-error); }
        .console .log-warning { color: var(--log-warning); }
        .console .log-system { color: var(--log-system); }

        .console .log-entry {
            animation: logIn 0.3s ease;
            padding: 0 4px;
            border-left: 2px solid transparent;
            transition: border-color 0.3s ease;
        }

        .console .log-entry:hover {
            border-left-color: var(--border-color);
        }

        @keyframes logIn {
            from { opacity: 0; transform: translateX(-8px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .full-width {
            grid-column: 1 / -1;
        }

        .footer {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 14px;
            margin-top: 28px;
            padding-top: 20px;
            border-top: 1px solid var(--footer-border);
            opacity: 0;
            animation: footerIn 0.8s ease-out 1s forwards;
        }

        @keyframes footerIn {
            to { opacity: 1; }
        }

        .footer .dots {
            display: flex;
            gap: 5px;
        }

        .footer .dot {
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--dot-bg);
            animation: dotPulse 2.5s ease-in-out infinite;
        }

        .footer .dot:nth-child(2) { animation-delay: 0.3s; }
        .footer .dot:nth-child(3) { animation-delay: 0.6s; }

        @keyframes dotPulse {
            0%, 100% { opacity: 0.2; transform: scale(0.8); }
            50% { opacity: 0.6; transform: scale(1.2); }
        }

        .footer span {
            color: var(--footer-text);
            font-size: 9px;
            letter-spacing: 2.5px;
            font-weight: 300;
            text-transform: uppercase;
        }

        @media (max-width: 1024px) {
            .grid { grid-template-columns: 1fr; }
            .container { padding: 28px 24px 22px; }
        }

        @media (max-width: 640px) {
            .container {
                padding: 18px 16px 16px;
                border-radius: 20px;
            }
            .header h1 {
                font-size: 20px;
                letter-spacing: 4px;
            }
            .header .logo-icon { font-size: 28px; }
            .stats { grid-template-columns: 1fr 1fr; }
            .btn {
                padding: 8px 14px;
                font-size: 9px;
                letter-spacing: 1.5px;
                flex: 1;
                min-width: 60px;
            }
            .drop-zone { padding: 28px 14px; }
            .drop-zone .icon-drop { font-size: 34px; }
            .panel { padding: 18px 16px 22px; }
            .file-info { flex-wrap: wrap; gap: 4px; }
            .file-info .name { font-size: 13px; }
            .theme-toggle {
                width: 40px;
                height: 40px;
                font-size: 18px;
                top: 12px;
                right: 12px;
            }
        }

        @media (max-width: 400px) {
            .stats { grid-template-columns: 1fr; }
            .header h1 { font-size: 16px; letter-spacing: 2px; }
            .header .subtitle { font-size: 9px; letter-spacing: 1.5px; }
            .btn-group { flex-direction: column; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>

    <div class="theme-toggle" id="themeToggle" title="Cambiar tema">
        <span id="themeIcon">🌙</span>
    </div>

    <div class="bg-pattern">
        <div class="grid"></div>
    </div>

    <div class="container">

        <div class="header">
            <div class="logo-wrap">
                <span class="logo-icon">⚡</span>
                <h1><span class="highlight">NUKKIT</span> COMPILER</h1>
            </div>
            <p class="subtitle">Compila tu plugin .zip a .jar en segundos</p>
            <div class="divider"></div>
        </div>

        <div class="grid">

            <div class="panel">
                <div class="panel-title">
                    <span class="icon-title">📦</span>
                    ARCHIVO ZIP
                    <span class="badge">.zip</span>
                </div>

                <div class="drop-zone" id="dropZone">
                    <span class="icon-drop">📂</span>
                    <p>Arrastra tu archivo <strong>.zip</strong> aquí</p>
                    <p class="sub-text">o haz clic para seleccionar</p>
                    <input type="file" id="fileInput" accept=".zip">
                </div>

                <div class="file-info" id="fileInfo">
                    <span class="name" id="fileName">archivo.zip</span>
                    <span class="status-badge loaded" id="statusBadge">✓ CARGADO</span>
                    <span class="size" id="fileSize">0 KB</span>
                </div>

                <div class="plugin-name-display" id="pluginNameDisplay">
                    <span class="label">📌 PLUGIN</span>
                    <span class="value" id="pluginNameValue">-</span>
                </div>

                <div class="file-list" id="fileList"></div>

                <div class="btn-group">
                    <button class="btn btn-primary" onclick="compileZip()">⟳ COMPILAR</button>
                    <button class="btn btn-success" onclick="downloadJar()">⬇ DESCARGAR</button>
                    <button class="btn btn-danger" onclick="clearConsole()">✕ LIMPIAR</button>
                </div>

                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar"><div class="fill" id="progressFill"></div></div>
                    <div class="progress-text" id="progressText">0%</div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-title">
                    <span class="icon-title">📊</span>
                    ESTADÍSTICAS
                    <span class="badge">info</span>
                </div>

                <div class="jar-name-display">
                    <span class="label">📦 JAR FINAL</span>
                    <span class="name" id="jarName">-</span>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="value" id="fileCount">0</div>
                        <div class="label">Archivos</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="classCount">0</div>
                        <div class="label">Clases</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="jarSize">0 KB</div>
                        <div class="label">Tamaño JAR</div>
                    </div>
                </div>

                <button class="btn btn-success" onclick="downloadJar()" style="width:100%;justify-content:center; padding:12px;">
                    ⬇ DESCARGAR .JAR
                </button>
            </div>

            <div class="panel full-width">
                <div class="panel-title">
                    <span class="icon-title">⌨</span>
                    CONSOLA
                    <span class="badge">output</span>
                </div>
                <div class="console" id="console">
                    <div class="log-entry log-system">[SISTEMA] Compilador listo</div>
                    <div class="log-entry log-system">[SISTEMA] Carga un archivo .zip para comenzar</div>
                </div>
            </div>

        </div>

        <div class="footer">
            <div class="dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
            <span>Compilación segura · Código abierto</span>
            <div class="dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        </div>

    </div>

    <script>
        (function() {
            const toggle = document.getElementById('themeToggle');
            const icon = document.getElementById('themeIcon');
            const html = document.documentElement;

            let currentTheme = localStorage.getItem('nukkit-theme') || 'light';
            html.setAttribute('data-theme', currentTheme);
            icon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';

            toggle.addEventListener('click', function() {
                const isDark = html.getAttribute('data-theme') === 'dark';
                const newTheme = isDark ? 'light' : 'dark';
                html.setAttribute('data-theme', newTheme);
                icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
                localStorage.setItem('nukkit-theme', newTheme);
            });
        })();

        var currentZip = null;
        var currentPluginName = 'plugin';
        var fileList = [];

        var dropZone = document.getElementById('dropZone');
        var fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', function() {
            fileInput.click();
        });

        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', function() {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            var files = e.dataTransfer.files;
            if (files.length > 0 && files[0].name.endsWith('.zip')) {
                handleFile(files[0]);
            } else {
                log('[ERROR] Solo se aceptan archivos .zip', 'error');
            }
        });

        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            currentZip = file;
            var info = document.getElementById('fileInfo');
            info.style.display = 'flex';
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = (file.size / 1024).toFixed(1) + ' KB';
            log('[SISTEMA] Archivo cargado: ' + file.name, 'success');

            var formData = new FormData();
            formData.append('file', file);

            fetch('/listzip', {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    fileList = data.files;
                    updateFileList();
                    document.getElementById('fileCount').textContent = data.files.length;

                    var classCount = 0;
                    data.files.forEach(function(f) {
                        if (f.name.endsWith('.class')) classCount++;
                    });
                    document.getElementById('classCount').textContent = classCount;

                    if (data.pluginName) {
                        currentPluginName = data.pluginName;
                        document.getElementById('pluginNameDisplay').style.display = 'flex';
                        document.getElementById('pluginNameValue').textContent = data.pluginName;
                        document.getElementById('jarName').textContent = data.pluginName + '.jar';
                    }
                }
            })
            .catch(function(error) {
                log('[ERROR] ' + error.message, 'error');
            });
        }

        function updateFileList() {
            var list = document.getElementById('fileList');
            list.innerHTML = '';
            fileList.forEach(function(file) {
                var div = document.createElement('div');
                div.className = 'file-item';
                var type = file.name.split('.').pop().toUpperCase();
                div.innerHTML = '<span>' + file.name + '</span><span><span class="type">' + type + '</span> <span class="size">' + file.size + '</span></span>';
                list.appendChild(div);
            });
        }

        function log(message, type) {
            type = type || 'info';
            var consoleEl = document.getElementById('console');
            var div = document.createElement('div');
            div.className = 'log-entry log-' + type;
            div.textContent = message;
            consoleEl.appendChild(div);
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }

        function clearConsole() {
            document.getElementById('console').innerHTML = '';
            log('[SISTEMA] Consola limpiada', 'system');
        }

        function showProgress(percent) {
            var container = document.getElementById('progressContainer');
            var fill = document.getElementById('progressFill');
            var text = document.getElementById('progressText');
            container.style.display = 'block';
            fill.style.width = percent + '%';
            text.textContent = Math.round(percent) + '%';
            if (percent >= 100) {
                setTimeout(function() { container.style.display = 'none'; }, 1500);
            }
        }

        function compileZip() {
            if (!currentZip) {
                log('[ERROR] No hay archivo .zip cargado', 'error');
                return;
            }

            log('[COMPILANDO] Iniciando compilación...', 'info');
            showProgress(10);

            var formData = new FormData();
            formData.append('file', currentZip);

            showProgress(20);

            fetch('/compilezip', {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                showProgress(100);
                if (data.success) {
                    log('[✓] COMPILACIÓN EXITOSA', 'success');
                    log('[✓] ' + data.message, 'success');
                    if (data.classes) {
                        document.getElementById('classCount').textContent = data.classes;
                    }
                    if (data.size) {
                        document.getElementById('jarSize').textContent = data.size;
                    }
                    if (data.jarName) {
                        document.getElementById('jarName').textContent = data.jarName;
                    }
                } else {
                    log('[✗] ERROR DE COMPILACIÓN', 'error');
                    log('[✗] ' + data.message, 'error');
                }
            })
            .catch(function(error) {
                showProgress(100);
                log('[✗] ERROR: ' + error.message, 'error');
            });
        }

        function downloadJar() {
            log('[DESCARGANDO] Preparando descarga...', 'info');
            window.location.href = '/download';
        }

        log('[SISTEMA] Compilador listo para usar', 'system');
        log('[SISTEMA] Carga un archivo .zip para comenzar', 'system');
    </script>

</body>
</html>
"""


def parse_plugin_yml(content):
    name = None
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('name:'):
            name = line.split('name:')[1].strip()
            break
    return name


def parse_multipart(data, boundary):
    parts = data.split(b'--' + boundary.encode())
    result = {}
    for part in parts:
        if not part or part == b'--\r\n':
            continue
        if b'\r\n\r\n' not in part:
            continue
        headers, content = part.split(b'\r\n\r\n', 1)
        content = content.rstrip(b'\r\n--')
        headers = headers.decode()
        if 'Content-Disposition' in headers:
            for line in headers.split('\r\n'):
                if 'name="' in line:
                    name = line.split('name="')[1].split('"')[0]
                    if 'filename="' in line:
                        filename = line.split('filename="')[1].split('"')[0]
                        result[name] = {'content': content, 'filename': filename}
                    else:
                        result[name] = content.decode()
    return result


def es_basura(nombre):
    return '__MACOSX' in nombre or nombre.endswith('.DS_Store') or nombre.endswith('/')


def destino_recurso(build_dir, work_dir, ruta_absoluta):
    rel = os.path.relpath(ruta_absoluta, work_dir)
    partes = rel.split(os.sep)
    if 'src' in partes:
        idx = partes.index('src')
        partes = partes[idx + 1:]
    if not partes:
        partes = [os.path.basename(rel)]
    return os.path.join(build_dir, *partes)


class CompilerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/download':
            self.send_response(200)
            self.send_header('Content-type', 'application/java-archive')
            jar_name = 'plugin.jar'
            if os.path.exists('plugin_name.txt'):
                with open('plugin_name.txt', 'r') as f:
                    name = f.read().strip()
                    if name:
                        jar_name = name + '.jar'
            self.send_header('Content-Disposition', 'attachment; filename="' + jar_name + '"')
            self.end_headers()
            if os.path.exists('plugin.jar'):
                with open('plugin.jar', 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'No JAR available')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/listzip':
            self._listzip()
        elif self.path == '/compilezip':
            self._compilezip()
        else:
            self.send_response(404)
            self.end_headers()

    def _listzip(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                self.send_response(400)
                self.end_headers()
                return

            boundary = content_type.split('boundary=')[1]
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)

            parsed = parse_multipart(raw_data, boundary)
            file_data = parsed.get('file')

            if not file_data:
                self._json({'success': False, 'message': 'No file'})
                return

            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp.write(file_data['content'])
                tmp_path = tmp.name

            files = []
            plugin_name = None

            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    if info.is_dir() or es_basura(info.filename):
                        continue
                    files.append({'name': info.filename, 'size': f'{info.file_size/1024:.1f} KB'})
                    if info.filename.endswith('plugin.yml'):
                        content = zip_ref.read(info.filename).decode('utf-8', errors='ignore')
                        plugin_name = parse_plugin_yml(content)

            os.unlink(tmp_path)

            if plugin_name:
                with open('plugin_name.txt', 'w') as f:
                    f.write(plugin_name)

            self._json({'success': True, 'files': files, 'pluginName': plugin_name})

        except Exception as e:
            self._json({'success': False, 'message': str(e)})

    def _compilezip(self):
        temp_dir = None
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                self.send_response(400)
                self.end_headers()
                return

            boundary = content_type.split('boundary=')[1]
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)

            parsed = parse_multipart(raw_data, boundary)
            file_data = parsed.get('file')

            if not file_data:
                self._json({'success': False, 'message': 'No file'})
                return

            temp_dir = tempfile.mkdtemp()
            work_dir = os.path.join(temp_dir, 'plugin')
            os.makedirs(work_dir, exist_ok=True)

            zip_path = os.path.join(temp_dir, 'plugin.zip')
            with open(zip_path, 'wb') as f:
                f.write(file_data['content'])

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(work_dir)

            plugin_name = None
            yml_path = None
            for root, dirs, files in os.walk(work_dir):
                if '__MACOSX' in root:
                    continue
                for file in files:
                    if file == 'plugin.yml':
                        yml_path = os.path.join(root, file)
                        with open(yml_path, 'r', encoding='utf-8', errors='ignore') as f:
                            plugin_name = parse_plugin_yml(f.read())
                        break
                if yml_path:
                    break

            if not plugin_name:
                plugin_name = 'plugin'

            java_files = []
            recursos = []
            for root, dirs, files in os.walk(work_dir):
                if '__MACOSX' in root:
                    continue
                for file in files:
                    if es_basura(file):
                        continue
                    full_path = os.path.join(root, file)
                    if file.endswith('.java'):
                        java_files.append(full_path)
                    elif file != 'nukkit.jar':
                        recursos.append(full_path)

            if not java_files:
                self._json({'success': False, 'message': 'No se encontraron archivos .java en el zip'})
                return

            build_dir = os.path.join(temp_dir, 'build')
            os.makedirs(build_dir, exist_ok=True)

            nukkit_jar = os.path.abspath('nukkit.jar')
            if not os.path.exists(nukkit_jar):
                nukkit_jar_in_zip = None
                for root, dirs, files in os.walk(work_dir):
                    if 'nukkit.jar' in files:
                        nukkit_jar_in_zip = os.path.join(root, 'nukkit.jar')
                        break
                if nukkit_jar_in_zip:
                    nukkit_jar = nukkit_jar_in_zip
                else:
                    self._json({'success': False, 'message': 'No se encontró nukkit.jar. Coloca nukkit.jar en el directorio o dentro del zip'})
                    return

            compile_args = ['javac', '-encoding', 'UTF-8', '-cp', nukkit_jar, '-d', build_dir] + java_files
            result = subprocess.run(compile_args, capture_output=True, text=True)

            if result.returncode != 0:
                self._json({'success': False, 'message': result.stderr or result.stdout or 'Error de compilación'})
                return

            for recurso in recursos:
                destino = destino_recurso(build_dir, work_dir, recurso)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.copy2(recurso, destino)

            plugin_yml_dest = os.path.join(build_dir, 'plugin.yml')
            if not os.path.exists(plugin_yml_dest):
                with open(plugin_yml_dest, 'w', encoding='utf-8') as f:
                    f.write(f'name: {plugin_name}\napi: ["1.0.0"]\nmain: Main\nversion: "1.0.0"\n')

            class_files = []
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    if file.endswith('.class'):
                        class_files.append(os.path.join(root, file))

            jar_path = os.path.join(temp_dir, plugin_name + '.jar')
            jar_args = ['jar', 'cvf', jar_path, '-C', build_dir, '.']
            subprocess.run(jar_args, capture_output=True, text=True)

            if os.path.exists('plugin.jar'):
                os.remove('plugin.jar')
            shutil.copy2(jar_path, 'plugin.jar')

            with open('plugin_name.txt', 'w') as f:
                f.write(plugin_name)

            size = os.path.getsize('plugin.jar') if os.path.exists('plugin.jar') else 0
            size_kb = f'{size/1024:.1f} KB'

            self._json({
                'success': True,
                'message': 'Plugin compilado exitosamente. ' + str(len(class_files)) + ' clases y ' + str(len(recursos) + 1) + ' recursos empaquetados.',
                'classes': len(class_files),
                'size': size_kb,
                'jarName': plugin_name + '.jar'
            })

        except Exception as e:
            self._json({'success': False, 'message': str(e)})
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def encontrar_puerto_libre(puerto_inicio):
    puerto = puerto_inicio
    while puerto <= MAX_PUERTO:
        try:
            with socketserver.TCPServer(('', puerto), CompilerHandler) as test_server:
                test_server.server_close()
                return puerto
        except OSError:
            puerto += 1
    return None


def abrir_chrome(puerto):
    time.sleep(2)
    url = f'http://localhost:{puerto}'
    sistema = detectar_sistema()

    if sistema == 'termux':
        try:
            os.system(f'termux-open-url "{url}"')
            print(f'✅ Abriendo Chrome (Termux): {url}')
            return
        except Exception as e:
            print(f'📡 Abre manualmente: {url} ({e})')
            return

    if sistema == 'windows':
        rutas_chrome = [
            os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
        ]
        chrome_exe = next((r for r in rutas_chrome if os.path.exists(r)), None)
        try:
            if chrome_exe:
                subprocess.Popen([chrome_exe, url])
                print(f'✅ Abriendo Chrome (Windows): {url}')
            else:
                os.startfile(url)
                print(f'✅ Abriendo navegador predeterminado (Windows): {url}')
        except Exception as e:
            print(f'📡 Abre manualmente: {url} ({e})')
        return

    try:
        webbrowser.open(url)
        print(f'✅ Abriendo navegador: {url}')
    except Exception as e:
        print(f'📡 Abre manualmente: {url} ({e})')


if __name__ == '__main__':
    if not verificar_dependencias():
        print("❌ Error al verificar dependencias")
        sys.exit(1)

    if not verificar_nukkit_jar():
        print("❌ No se encontró nukkit.jar")
        print("   Coloca nukkit.jar en la carpeta o descárgalo manualmente")
        sys.exit(1)

    print('🔍 Buscando puerto libre desde ' + str(INICIO_PUERTO) + '...')
    puerto = encontrar_puerto_libre(INICIO_PUERTO)

    if puerto is None:
        print('❌ No se encontró puerto libre')
        sys.exit(1)

    sistema = detectar_sistema()
    print('')
    print('    ╔═══════════════════════════════════════════╗')
    print('    ║   🚀 NUKKIT COMPILER PRO                 ║')
    print('    ║   📡 http://localhost:' + str(puerto) + '            ║')
    print('    ║   🖥️  Sistema: ' + sistema.ljust(28) + '║')
    print('    ║   🌐 Abriendo navegador...               ║')
    print('    ║   ⏹️  Ctrl+C para detener                 ║')
    print('    ╚═══════════════════════════════════════════╝')
    print('')

    threading.Thread(target=abrir_chrome, args=(puerto,), daemon=True).start()

    try:
        with socketserver.TCPServer(('', puerto), CompilerHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print('\n👋 Servidor detenido')
                httpd.shutdown()
    except OSError as e:
        print('\n❌ Error: ' + str(e))
