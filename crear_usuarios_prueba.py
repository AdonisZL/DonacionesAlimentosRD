#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crear usuarios de prueba para la presentación del sistema
Genera hashes bcrypt válidos e inserta en la BD
"""

import sys
import os
from pathlib import Path

# Agregar el backend al path
sys.path.insert(0, str(Path(__file__).parent / "DonacionesAlimentosRD" / "backend"))

import bcrypt
from sqlalchemy import text, select
from app.database.conexion import motor, SessionLocal
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.direcciones_sedes import DireccionesSedes
from app.models.perfiles_legales import PerfilLegal

def hashear_contrasena(contrasena: str) -> str:
    """Genera hash bcrypt de una contraseña"""
    sal = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("utf-8")

def crear_usuarios_prueba():
    """Crea 4 usuarios de prueba para la demostración"""
    
    # Datos de usuarios a crear
    usuarios_datos = [
        {
            "nombre": "Admin",
            "apellido": "Sistema",
            "email": "admin@donacionesalimentos.com",
            "contrasena": "Admin123!",
            "rol_nombre": "administrador",
            "telefono": "+1-809-000-0001",
            "estado": "activo",
            "subtipo_donante": None,
        },
        {
            "nombre": "Carlos",
            "apellido": "Martínez",
            "email": "banco@donacionesalimentos.com",
            "contrasena": "Banco123!",
            "rol_nombre": "banco_alimentos",
            "telefono": "+1-809-000-0002",
            "estado": "activo",
            "subtipo_donante": None,
        },
        {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "donante@supermercado.com.do",
            "contrasena": "Donante123!",
            "rol_nombre": "donante",
            "telefono": "+1-809-000-0003",
            "estado": "activo",
            "subtipo_donante": "formal",
        },
        {
            "nombre": "María",
            "apellido": "González",
            "email": "receptor@fundacion.com.do",
            "contrasena": "Receptor123!",
            "rol_nombre": "receptor",
            "telefono": "+1-809-000-0004",
            "estado": "activo",
            "subtipo_donante": None,
        },
    ]
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Creando Usuarios de Prueba para Presentación             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    session = SessionLocal()
    try:
        usuarios_creados = []
        
        for datos in usuarios_datos:
            try:
                # Verificar si el usuario ya existe
                usuario_existente = session.execute(
                    select(Usuario).where(Usuario.email == datos["email"])
                ).scalar()
                
                if usuario_existente:
                    print(f"⚠️  Usuario {datos['email']} ya existe, omitiendo...")
                    continue
                
                # Obtener el rol
                rol = session.execute(
                    select(Rol).where(Rol.nombre == datos["rol_nombre"])
                ).scalar()
                
                if not rol:
                    print(f"❌ Rol '{datos['rol_nombre']}' no encontrado")
                    continue
                
                # Crear el usuario
                hash_contrasena = hashear_contrasena(datos["contrasena"])
                
                nuevo_usuario = Usuario(
                    nombre=datos["nombre"],
                    apellido=datos["apellido"],
                    email=datos["email"],
                    contrasena_hash=hash_contrasena,
                    id_rol=rol.id_rol,
                    telefono=datos["telefono"],
                    estado=datos["estado"],
                    email_verificado=True,
                    subtipo_donante=datos["subtipo_donante"],
                )
                
                session.add(nuevo_usuario)
                session.flush()  # Obtener el ID generado
                
                usuarios_creados.append({
                    "usuario": nuevo_usuario,
                    "contrasena": datos["contrasena"],
                    "rol": datos["rol_nombre"],
                })
                
                print(f"✅ Creado: {datos['nombre']} ({datos['rol_nombre']})")
                
            except Exception as e:
                print(f"❌ Error creando usuario {datos['email']}: {str(e)}")
                session.rollback()
                continue
        
        # Crear sedes para banco y receptor
        print()
        print("Creando sedes/direcciones...")
        
        for usuario_data in usuarios_creados:
            usuario = usuario_data["usuario"]
            
            if usuario_data["rol"] == "banco_alimentos":
                sede = DireccionesSedes(
                    id_usuario=usuario.id_usuario,
                    nombre_sede="Sede Central Banco de Alimentos",
                    direccion_texto="Avenida 27 de Febrero #123, Santo Domingo, RD",
                    correo_contacto=usuario.email,
                    telefono_contacto=usuario.telefono,
                    coordenadas="POINT(-69.9312 18.4861)",
                    capacidad_diaria_kg=5000.00,
                    tiene_cadena_frio=True,
                    estado="activa",
                )
                session.add(sede)
                print(f"✅ Sede creada para Banco de Alimentos")
                
            elif usuario_data["rol"] == "receptor":
                sede = DireccionesSedes(
                    id_usuario=usuario.id_usuario,
                    nombre_sede="Centro de Distribución Fundación",
                    direccion_texto="Calle Conde #456, Santo Domingo, RD",
                    correo_contacto=usuario.email,
                    telefono_contacto=usuario.telefono,
                    coordenadas="POINT(-69.9288 18.4898)",
                    capacidad_diaria_kg=2000.00,
                    tiene_cadena_frio=False,
                    estado="activa",
                )
                session.add(sede)
                print(f"✅ Sede creada para Receptor")
        
        session.commit()
        
        # Mostrar credenciales
        print()
        print("═" * 60)
        print("CREDENCIALES DE PRUEBA")
        print("═" * 60)
        print()
        
        for usuario_data in usuarios_creados:
            usuario = usuario_data["usuario"]
            rol_display = usuario_data["rol"].upper().replace("_", " ")
            
            print(f"👤 {rol_display}")
            print(f"   Email:      {usuario.email}")
            print(f"   Contraseña: {usuario_data['contrasena']}")
            print(f"   Teléfono:   {usuario.telefono}")
            print()
        
        print("═" * 60)
        print(f"✅ {len(usuarios_creados)} usuarios creados exitosamente")
        print("═" * 60)
        print()
        print("🚀 Ahora puedes iniciar sesión en http://localhost:8000/docs")
        print("   o en tu aplicación frontend con estas credenciales")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    try:
        exito = crear_usuarios_prueba()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
