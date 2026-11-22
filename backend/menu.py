# -*- coding: utf-8 -*-
"""Menú demo de comida costera - Puerto A&M Gourmet (Paraíso, Tabasco)."""
MENU = {
    "entradas": [
        {"id": "E1", "nombre": "Ceviche de pescado del día", "desc": "Pescado fresco marinado en limón, con jitomate, cebolla, cilantro y aguacate. Fresco y ligero.", "precio": 185},
        {"id": "E2", "nombre": "Tostadas de atún", "desc": "Atún marinado sobre tostada crujiente con aguacate y salsa de soya-limón.", "precio": 165},
        {"id": "E3", "nombre": "Ostiones frescos (6 pzas)", "desc": "Ostiones del Golfo servidos en su concha, con limón y salsa picante.", "precio": 220},
        {"id": "E4", "nombre": "Camarones aguachile", "desc": "Camarones frescos en salsa de chile serrano y limón, con pepino y cebolla morada.", "precio": 210},
    ],
    "platos_fuertes": [
        {"id": "P1", "nombre": "Pescado a la talla", "desc": "Pescado entero asado a la leña con salsa de chile guajillo y achiote. ¡Nuestro favorito!", "precio": 320},
        {"id": "P2", "nombre": "Huachinango a la sal", "desc": "Huachinango entero horneado en costra de sal, jugoso y aromático.", "precio": 390},
        {"id": "P3", "nombre": "Camarones al coco", "desc": "Camarones empanizados en coco, fritos, con salsa de mango y chile. Dulce y crujiente.", "precio": 260},
        {"id": "P4", "nombre": "Arroz a la tumbada", "desc": "Arroz caldoso con mariscos variados: camarón, pulpo, jaiba y mejillones.", "precio": 240},
        {"id": "P5", "nombre": "Mojarra frita", "desc": "Mojarra entera frita, crujiente por fuera y suave por dentro, con ensalada.", "precio": 230},
        {"id": "P6", "nombre": "Caldo de mariscos", "desc": "Caldo rico y reconfortante con camarón, pulpo, jaiba y verduras. Ideal para compartir.", "precio": 195},
        {"id": "P7", "nombre": "Filete de pescado al mojo de ajo", "desc": "Filete de pescado salteado en mantequilla y ajo, con arroz y ensalada.", "precio": 250},
    ],
    "tacos": [
        {"id": "T1", "nombre": "Tacos de camarón (3 pzas)", "desc": "Tacos de camarón empanizado con repollo, salsa chipotle y limón.", "precio": 150},
        {"id": "T2", "nombre": "Tacos de pescado (3 pzas)", "desc": "Tacos de pescado capeado con ensalada de col y salsa de anguila.", "precio": 135},
    ],
    "bebidas": [
        {"id": "B1", "nombre": "Agua fresca (limón/jamaica)", "desc": "Refrescante y natural.", "precio": 45},
        {"id": "B2", "nombre": "Refresco", "desc": "Coca-Cola, Sprite o Fanta.", "precio": 40},
        {"id": "B3", "nombre": "Cerveza (varias)", "desc": "Corona, Victoria o Modelo.", "precio": 65},
        {"id": "B4", "nombre": "Michelada", "desc": "Cerveza preparada con limón, sal y salsas. ¡La favorita!", "precio": 85},
    ],
    "postres": [
        {"id": "D1", "nombre": "Flan de coco", "desc": "Flan suave con toque de coco y caramelo.", "precio": 75},
        {"id": "D2", "nombre": "Pastel de queso", "desc": "Cheesecake casero con frutos rojos.", "precio": 80},
    ],
}

def menu_text():
    lines = []
    for cat, items in MENU.items():
        lines.append(f"--- {cat.upper().replace('_',' ')} ---")
        for it in items:
            lines.append(f"{it['id']}: {it['nombre']} - {it['desc']} (Precio: ${it['precio']} MXN)")
    return "\n".join(lines)

def menu_flat():
    out = []
    for cat, items in MENU.items():
        for it in items:
            out.append({"categoria": cat, **it})
    return out
