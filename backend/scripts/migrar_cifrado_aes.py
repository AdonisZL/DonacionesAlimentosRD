"""Migración de datos existentes a AES-256 / 现有数据 AES-256 加密迁移.

Cifra los RNC que actualmente están en texto claro en la tabla `perfiles_legales`
y en `direcciones_sedes`.
加密 `perfiles_legales` 和 `direcciones_sedes` 表中当前以明文存储的 RNC。

Uso / 用法:
    python scripts/migrar_cifrado_aes.py

Precaución / 注意:
    - Hacer respaldo de la BD antes de ejecutar / 运行前请备份数据库.
    - Una vez cifrados, los datos solo se pueden leer con la misma CLAVE_AES256.
      加密后只能用相同的 CLAVE_AES256 读取.
"""

import sys
from pathlib import Path

# Agregar backend al path / 将 backend 添加到路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config.configuracion import configuracion  # noqa: E402
from app.database.conexion import SesionLocal  # noqa: E402
from app.models.direccion_sede import DireccionSede  # noqa: E402
from app.models.perfil_legal import PerfilLegal  # noqa: E402
from app.utils.cifrado import cifrar_aes256, configurar_clave_aes  # noqa: E402


def migrar():
    """Cifra todos los RNC en texto claro / 加密所有明文 RNC."""
    if not configuracion.clave_aes256:
        print("ERROR: CLAVE_AES256 no está configurada en .env")
        print(
            'Genera una con: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"'
        )
        sys.exit(1)

    configurar_clave_aes(configuracion.clave_aes256)

    sesion = SesionLocal()
    try:
        # 1. Cifrar RNC en perfiles_legales / 加密法律信息中的 RNC
        perfiles = sesion.query(PerfilLegal).filter(PerfilLegal.rnc.isnot(None)).all()
        cifrados_perfil = 0
        for perfil in perfiles:
            if not perfil.rnc:
                continue
            # Verificar si ya está cifrado (base64 sin caracteres no-ASCII)
            # 检查是否已加密（base64 不含非 ASCII 字符）
            try:
                rnc_original = perfil.rnc
                if rnc_original.isdigit() and len(rnc_original) == 11:
                    # Es un RNC en texto claro (11 dígitos) / 是明文 RNC（11 位数字）
                    perfil.rnc = cifrar_aes256(rnc_original)
                    cifrados_perfil += 1
                    print(f"  ✓ Cifrado RNC en perfil_legal: {rnc_original[:3]}***")
            except Exception as e:
                print(
                    f"  ✗ Error cifrando RNC en perfil_legal {perfil.id_usuario}: {e}"
                )

        # 2. Cifrar RNC en direcciones_sedes / 加密场所地址中的 RNC
        sedes = sesion.query(DireccionSede).filter(DireccionSede.rnc.isnot(None)).all()
        cifrados_sede = 0
        for sede in sedes:
            if not sede.rnc:
                continue
            try:
                rnc_original = sede.rnc
                if rnc_original.isdigit() and len(rnc_original) == 11:
                    sede.rnc = cifrar_aes256(rnc_original)
                    cifrados_sede += 1
                    print(f"  ✓ Cifrado RNC en direccion_sede: {rnc_original[:3]}***")
            except Exception as e:
                print(f"  ✗ Error cifrando RNC en direccion_sede {sede.id_sede}: {e}")

        sesion.commit()
        print(f"\n✅ Migración completada:")
        print(f"   RNC cifrados en perfiles_legales: {cifrados_perfil}")
        print(f"   RNC cifrados en direcciones_sedes: {cifrados_sede}")
        print(
            f"\n⚠️  Guarda la CLAVE_AES256 en un lugar seguro. Sin ella no podrás leer los RNC."
        )

    except Exception as e:
        sesion.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
    finally:
        sesion.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migración AES-256 — Cifrado de RNC existentes")
    print("AES-256 迁移 — 加密现有 RNC")
    print("=" * 60)
    print(
        f"Base de datos: {configuracion.bd_host}:{configuracion.bd_puerto}/{configuracion.bd_nombre}"
    )
    print()
    respuesta = input("¿Has hecho un respaldo de la base de datos? (s/n): ")
    if respuesta.lower() != "s":
        print("Haz un respaldo antes de ejecutar este script. / 运行前请备份。")
        sys.exit(0)
    migrar()
