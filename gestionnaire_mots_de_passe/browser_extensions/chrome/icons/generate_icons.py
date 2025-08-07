#!/usr/bin/env python3
"""
Générateur d'icônes pour l'extension navigateur
Créer des icônes PNG de haute qualité pour le Gestionnaire de Mots de Passe
"""

import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_lock_icon_svg(size):
    """Créer une icône de cadenas en SVG"""
    # Couleurs du thème
    primary_color = "#4f46e5"  # Bleu cybersec
    secondary_color = "#7c3aed"  # Violet accent
    
    # Ajuster les proportions selon la taille
    if size <= 16:
        lock_size = size * 0.8
        stroke_width = 1
        font_size = size * 0.3
    elif size <= 32:
        lock_size = size * 0.75
        stroke_width = 1.5
        font_size = size * 0.25
    elif size <= 48:
        lock_size = size * 0.7
        stroke_width = 2
        font_size = size * 0.2
    else:  # 128px
        lock_size = size * 0.65
        stroke_width = 3
        font_size = size * 0.15
    
    # Centrage
    center_x = size / 2
    center_y = size / 2
    
    # Dimensions du cadenas
    lock_width = lock_size * 0.6
    lock_height = lock_size * 0.7
    lock_x = center_x - lock_width / 2
    lock_y = center_y - lock_height / 2 + lock_size * 0.1
    
    # Arc du cadenas (partie supérieure)
    arc_width = lock_width * 0.8
    arc_height = lock_height * 0.4
    arc_x = center_x - arc_width / 2
    arc_y = lock_y - arc_height * 0.6
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="lockGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{secondary_color};stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="rgba(79, 70, 229, 0.3)"/>
            </filter>
        </defs>
        
        <!-- Corps du cadenas -->
        <rect x="{lock_x}" y="{lock_y}" width="{lock_width}" height="{lock_height}" 
              rx="{lock_width * 0.1}" ry="{lock_width * 0.1}"
              fill="url(#lockGradient)" 
              filter="url(#shadow)" />
        
        <!-- Arc supérieur du cadenas -->
        <path d="M {arc_x + arc_width * 0.2} {arc_y + arc_height} 
                 Q {arc_x + arc_width * 0.2} {arc_y} {center_x} {arc_y}
                 Q {arc_x + arc_width * 0.8} {arc_y} {arc_x + arc_width * 0.8} {arc_y + arc_height}"
              stroke="url(#lockGradient)" 
              stroke-width="{stroke_width}" 
              fill="none" />
        
        <!-- Point de serrure -->
        <circle cx="{center_x}" cy="{center_y + lock_size * 0.05}" r="{stroke_width * 1.5}" 
                fill="white" opacity="0.9" />
        <rect x="{center_x - stroke_width * 0.5}" y="{center_y + lock_size * 0.05}" 
              width="{stroke_width}" height="{lock_size * 0.15}" 
              fill="white" opacity="0.9" />
    </svg>'''
    
    return svg_content

def svg_to_png(svg_content, size, output_path):
    """Convertir SVG en PNG en utilisant une approche alternative"""
    try:
        # Créer une image avec un fond transparent
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Couleurs
        primary = (79, 70, 229, 255)  # #4f46e5
        secondary = (124, 58, 237, 255)  # #7c3aed
        white = (255, 255, 255, 255)
        
        # Proportions
        center_x, center_y = size // 2, size // 2
        
        if size <= 16:
            lock_size = int(size * 0.8)
            stroke_width = 1
        elif size <= 32:
            lock_size = int(size * 0.75)
            stroke_width = 2
        elif size <= 48:
            lock_size = int(size * 0.7)
            stroke_width = 2
        else:  # 128px
            lock_size = int(size * 0.65)
            stroke_width = 3
        
        # Dimensions du cadenas
        lock_width = int(lock_size * 0.6)
        lock_height = int(lock_size * 0.7)
        lock_x = center_x - lock_width // 2
        lock_y = center_y - lock_height // 2 + int(lock_size * 0.1)
        
        # Corps du cadenas (rectangle avec coins arrondis)
        padding = 2
        for i in range(stroke_width):
            color_ratio = i / max(1, stroke_width - 1)
            r = int(primary[0] + (secondary[0] - primary[0]) * color_ratio)
            g = int(primary[1] + (secondary[1] - primary[1]) * color_ratio)
            b = int(primary[2] + (secondary[2] - primary[2]) * color_ratio)
            color = (r, g, b, 255)
            
            draw.rounded_rectangle(
                [lock_x + i, lock_y + i, lock_x + lock_width - i, lock_y + lock_height - i],
                radius=max(2, lock_width // 10),
                fill=color
            )
        
        # Arc supérieur (approximation avec des lignes)
        arc_width = int(lock_width * 0.8)
        arc_height = int(lock_height * 0.4)
        arc_x = center_x - arc_width // 2
        arc_y = lock_y - int(arc_height * 0.6)
        
        # Dessiner l'arc avec des segments
        for i in range(stroke_width):
            # Côtés gauche et droit de l'arc
            draw.line([arc_x + arc_width // 4, arc_y + arc_height, 
                      arc_x + arc_width // 4, arc_y + arc_height // 3], 
                     fill=primary, width=stroke_width)
            draw.line([arc_x + 3 * arc_width // 4, arc_y + arc_height, 
                      arc_x + 3 * arc_width // 4, arc_y + arc_height // 3], 
                     fill=primary, width=stroke_width)
            # Partie supérieure de l'arc
            draw.arc([arc_x + arc_width // 4, arc_y, 
                     arc_x + 3 * arc_width // 4, arc_y + arc_height // 2], 
                    0, 180, fill=primary, width=stroke_width)
        
        # Point de serrure
        keyhole_radius = max(2, stroke_width)
        draw.ellipse([center_x - keyhole_radius, center_y - keyhole_radius + int(lock_size * 0.05),
                     center_x + keyhole_radius, center_y + keyhole_radius + int(lock_size * 0.05)],
                    fill=white)
        
        # Fente de la serrure
        slot_width = max(1, stroke_width // 2)
        slot_height = int(lock_size * 0.15)
        draw.rectangle([center_x - slot_width, center_y + int(lock_size * 0.05),
                       center_x + slot_width, center_y + int(lock_size * 0.05) + slot_height],
                      fill=white)
        
        # Sauvegarder
        img.save(output_path, 'PNG', optimize=True)
        print(f"✓ Icône {size}x{size} créée : {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Erreur pour {size}x{size}: {e}")
        return False

def generate_all_icons():
    """Générer toutes les tailles d'icônes"""
    sizes = [16, 32, 48, 128]
    icons_dir = "/app/gestionnaire_mots_de_passe/browser_extensions/chrome/icons"
    
    print("🎨 Génération des icônes pour l'extension...")
    
    success_count = 0
    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon{size}.png")
        
        # Générer le SVG
        svg_content = create_lock_icon_svg(size)
        
        # Convertir en PNG
        if svg_to_png(svg_content, size, output_path):
            success_count += 1
        
        # Nettoyer les anciens fichiers .txt
        txt_path = os.path.join(icons_dir, f"icon{size}.txt")
        if os.path.exists(txt_path):
            os.remove(txt_path)
            print(f"  🗑️ Supprimé {txt_path}")
    
    print(f"\n✅ {success_count}/{len(sizes)} icônes générées avec succès!")
    
    # Vérifier les tailles de fichiers
    print("\n📊 Tailles des fichiers:")
    for size in sizes:
        png_path = os.path.join(icons_dir, f"icon{size}.png")
        if os.path.exists(png_path):
            file_size = os.path.getsize(png_path)
            print(f"  icon{size}.png: {file_size:,} bytes")

if __name__ == "__main__":
    generate_all_icons()