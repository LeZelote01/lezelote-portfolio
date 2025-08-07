#!/usr/bin/env python3
"""
Générateur d'icônes pour l'extension Chrome
Crée des icônes PNG simples avec PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL/Pillow non disponible - création d'icônes de base")

import os

def create_simple_icon(size, output_path):
    """Crée une icône simple sans PIL"""
    # Créer un fichier SVG simple puis le convertir
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Fond circulaire -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2-2}" fill="url(#grad)" stroke="white" stroke-width="2"/>
  
  <!-- Icône de cadenas -->
  <g transform="translate({size//4}, {size//4})">
    <!-- Corps du cadenas -->
    <rect x="{size//8}" y="{size//4}" width="{size//4}" height="{size//4}" 
          fill="white" rx="2"/>
    
    <!-- Anse du cadenas -->
    <path d="M {size//6} {size//4} Q {size//4} {size//8} {size//3} {size//4}" 
          stroke="white" stroke-width="2" fill="none"/>
    
    <!-- Point du centre -->
    <circle cx="{size//4}" cy="{size//3}" r="2" fill="#667eea"/>
  </g>
</svg>'''
    
    # Sauvegarder le SVG temporairement
    svg_path = output_path.replace('.png', '.svg')
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ Icône SVG créée: {svg_path}")
    return svg_path

def create_icon_with_pil(size, output_path):
    """Crée une icône avec PIL/Pillow"""
    # Créer une image avec transparence
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs du gradient (approximation)
    color1 = (102, 126, 234)  # #667eea
    color2 = (118, 75, 162)   # #764ba2
    
    # Dessiner le fond circulaire avec gradient approximé
    for i in range(size):
        for j in range(size):
            # Calculer la distance au centre
            dx = i - size // 2
            dy = j - size // 2
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= size // 2 - 2:
                # Gradient basé sur la position
                ratio = i / size
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                img.putpixel((i, j), (r, g, b, 255))
    
    # Dessiner le cadenas en blanc
    # Corps du cadenas
    rect_size = size // 3
    rect_x = (size - rect_size) // 2
    rect_y = size // 2
    draw.rectangle([rect_x, rect_y, rect_x + rect_size, rect_y + rect_size // 2], 
                   fill='white', outline='white')
    
    # Anse du cadenas (approximation avec arc)
    arc_size = rect_size // 2
    arc_x = rect_x + rect_size // 4
    arc_y = rect_y - arc_size // 2
    draw.arc([arc_x, arc_y, arc_x + arc_size, arc_y + arc_size], 
             start=0, end=180, fill='white', width=2)
    
    # Point central
    center_x, center_y = rect_x + rect_size // 2, rect_y + rect_size // 4
    draw.ellipse([center_x - 2, center_y - 2, center_x + 2, center_y + 2], 
                 fill=color1)
    
    # Sauvegarder
    img.save(output_path, 'PNG')
    print(f"✅ Icône PNG créée: {output_path}")

def generate_all_icons():
    """Génère toutes les tailles d'icônes requises"""
    icons_dir = os.path.dirname(os.path.abspath(__file__))
    sizes = [16, 32, 48, 128]
    
    print(f"🎨 Génération des icônes dans: {icons_dir}")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        
        if PIL_AVAILABLE:
            create_icon_with_pil(size, output_path)
        else:
            # Créer une version SVG comme fallback
            svg_path = create_simple_icon(size, output_path)
            print(f"💡 Convertissez {svg_path} en PNG avec un outil externe")
    
    print(f"\n🎉 {len(sizes)} icônes générées !")
    print("\n📁 Structure des icônes:")
    for size in sizes:
        print(f"   - icon{size}.png ({size}x{size})")

if __name__ == "__main__":
    generate_all_icons()