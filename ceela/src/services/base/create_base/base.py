from typing import List, Optional, Dict, Any, Union, Type
from sqlalchemy.orm import Session
from src.models.entity.detail_part import DetailPart
from src.models.entity.elements import Element
from src.models.entity.enclosure_general import EnclosureGeneralsCreate, EnclosureGenerals
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.entity.wall import WallEnclosure
from src.models.entity.door import DoorEnclosure
from src.models.entity.roof import RoofEnclosure
from src.models.entity.window import WindowEnclosure
from src.models.entity.floor import FloorEnclosure
from src.services.po.calculate_piso import calculate_termitancia_piso
from src.services.po.po_services import thermal_bridge_floor, thermal_bridges_wall, thermal_bridges_window
from src.services.tablas_py.tablas_py import calculate_tablas_py


def create_enclosure_base(original_enclosure_id: int, db: Session):
    try:
        print(f"📌 Buscando Enclosure con id={original_enclosure_id} y no eliminado...")
        enclosure_original = (
            db.query(EnclosureGenerals)
              .filter(
                  EnclosureGenerals.id == original_enclosure_id,
                  EnclosureGenerals.is_deleted == False
              )
              .first()
        )
        
        print("🔍 Registro encontrado:", enclosure_original)
        if not enclosure_original:
            print("❌ No se encontró el registro.")
            return None
        
        print("📦 Datos originales con model_dump (excluyendo id):")
        enclosure_base_data = enclosure_original.model_dump(exclude={"id"})
        print(enclosure_base_data)

        enclosure_base_data["name_enclosure"] = f"{enclosure_original.name_enclosure}-Base"
        print("✏️ Datos después de modificar name_enclosure:")
        print(enclosure_base_data)
        
        enclosure_base_data['is_base'] = True
        enclosure_base_data['original_enclosure_id'] = enclosure_original.id

        enclosure_table = EnclosureGenerals(
            **enclosure_base_data
        )
        print("🆕 Objeto EnclosureGenerals creado (sin guardar aún):", enclosure_table)

        db.add(enclosure_table)
        print("💾 Objeto añadido a la sesión.")

        db.commit()
        print("✅ Commit realizado.")

        db.refresh(enclosure_table)
        print("🔄 Registro refrescado desde la base de datos.")

        print("🎯 Resultado final:", enclosure_table)

    except Exception as e:
        db.rollback()
        print(f"💥 Error creando enclosure base: {e}")
     
        

def delete_enclosures_bases(original_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """
    Hard delete de TODOS los 'base' ligados a original_enclosure_id = original_id.
    No toca el registro original.
    """
    try:
        bases = (
            db.query(EnclosureGenerals)
              .filter(
                  EnclosureGenerals.original_enclosure_id == original_id,
                  EnclosureGenerals.is_base == True
              )
              .all()
        )

        if not bases:
            return {"deleted_count": 0, "deleted_base_ids": []}

        deleted_ids = [b.id for b in bases]
        for b in bases:
            db.delete(b)

        db.commit()
        return {"deleted_count": len(deleted_ids), "deleted_base_ids": deleted_ids}

    except Exception as e:
        db.rollback()
        print(f"Error al borrar bases de original_enclosure_id={original_id}: {e}")
        return None
    



def sync_enclosure_bases_debug(original_enclosure_id: int, db: Session) -> Optional[List[int]]:
    try:
        print(f"📌 Buscando ORIGINAL con id={original_enclosure_id} y no eliminado...")
        original = (
            db.query(EnclosureGenerals)
              .filter(
                  EnclosureGenerals.id == original_enclosure_id,
                  EnclosureGenerals.is_deleted.is_(False)
              )
              .first()
        )
        print("🔍 ORIGINAL encontrado:", original)
        if not original:
            print("❌ No se encontró el ORIGINAL.")
            return None

        if getattr(original, "is_base", False):
            print("⚠️ El id indicado pertenece a un BASE, no a un ORIGINAL. Abortando sync.")
            return None

        print("🔎 Buscando BASES ligados al ORIGINAL...")
        bases = (
            db.query(EnclosureGenerals)
              .filter(
                  EnclosureGenerals.original_enclosure_id == original.id,
                  EnclosureGenerals.is_base.is_(True),
                  EnclosureGenerals.is_deleted.is_(False)
              )
              .all()
        )
        print(f"🧮 BASES encontrados: {len(bases)} -> {[b.id for b in bases]}")
        if not bases:
            print("ℹ️ No hay BASES para sincronizar.")
            return []

        # Campos que se copiarán del ORIGINAL al BASE
        fields_to_copy = ("occupation_profile_id", "height", "co2_sensor", "level_id", "project_id")

        print("📦 Datos del ORIGINAL (model_dump):")
        original_data = original.model_dump()
        print({k: original_data.get(k) for k in fields_to_copy + ("name_enclosure",)})

        # Aplicar cambios en cada BASE
        updated_ids: List[int] = []
        for b in bases:
            print(f"\n🧩 Actualizando BASE id={b.id}...")
            before = b.model_dump()
            # Copiar campos
            for f in fields_to_copy:
                if hasattr(original, f):
                    setattr(b, f, getattr(original, f))
            # Renombrar con sufijo
            b.name_enclosure = f"{original.name_enclosure}-Base"

            after = b.model_dump()
            print("   ⬅️ Antes:", {k: before.get(k) for k in fields_to_copy + ("name_enclosure",)})
            print("   ➡️  Después:", {k: after.get(k) for k in fields_to_copy + ("name_enclosure",)})
            updated_ids.append(b.id)

        # Persistir cambios
        db.commit()
        print("✅ Commit realizado.")

        # Refrescar cada BASE
        for b in bases:
            db.refresh(b)
        print("🔄 BASES refrescados desde la base de datos.")

        print("🎯 BASES sincronizados:", updated_ids)
        return updated_ids

    except Exception as e:
        db.rollback()
        print(f"💥 Error al sincronizar BASES desde el ORIGINAL {original_enclosure_id}: {e}")
        return None
    
    
    
SpecificEnclosure = Union[WallEnclosure, DoorEnclosure, RoofEnclosure, WindowEnclosure, FloorEnclosure]
DEFAULT_AZIMUTH = "0° ≤ Az < 22,5°"
DEFAULT_ORIENTATION = "N"

def create_obj_base(enclosure_obj: SpecificEnclosure, db: Session) -> Optional[SpecificEnclosure]:
    try:
        if enclosure_obj is None:
            print("❌ No se recibió objeto a clonar.")
            return None

        cls: Type[SpecificEnclosure] = type(enclosure_obj)
        model_fields = getattr(cls, "model_fields", {})
        print(f"📌 Clonando {cls.__name__} id={getattr(enclosure_obj, 'id', None)}")

        # 1) Dump base sin PK
        data: Dict[str, Any] = enclosure_obj.model_dump(exclude={"id"})
        print("📦 Dump original (sin id):", data)

        # 2) Resolver ENCLOSURE BASE (para asignarlo al clon)
        enclosure_id_orig = data.get("enclosure_id") or getattr(enclosure_obj, "enclosure_id", None)
        if enclosure_id_orig is None:
            print("❌ El objeto original no tiene enclosure_id; no puedo mapear al enclosure base.")
            return None

        enc_orig = db.query(EnclosureGenerals).filter(EnclosureGenerals.id == enclosure_id_orig).first()
        print("🔎 Enclosure ORIGINAL:", enc_orig)
        if not enc_orig:
            print(f"❌ No existe EnclosureGenerals.id={enclosure_id_orig}")
            return None

        enc_base = (
            db.query(EnclosureGenerals)
              .filter(
                  EnclosureGenerals.original_enclosure_id == enclosure_id_orig,
                  EnclosureGenerals.is_base.is_(True),
                  EnclosureGenerals.is_deleted.is_(False)
              )
              .first()
        )
        print("🏷️ Enclosure BASE asociado:", enc_base)
        if not enc_base:
            print(f"❌ No existe Enclosure BASE para original_enclosure_id={enclosure_id_orig}.")
            return None

        # Usar SIEMPRE el enclosure_id del BASE para el clon
        data["enclosure_id"] = enc_base.id
        print(f"🔁 enclosure_id del clon -> {enc_base.id}")

        # Project id (para búsquedas de DetailPart/Element)
        project_id = getattr(enc_base, "project_id", None)
        print("📌 project_id (desde enclosure BASE):", project_id)

        # 3) Selección de IDs base según el tipo
        dp = None
        if isinstance(enclosure_obj, WallEnclosure):
            if project_id is None:
                print("❌ No hay project_id para 'Muro Base'.")
                return None
            dp = db.query(DetailPart).filter(
                DetailPart.name_detail == "Muro Base",
                DetailPart.project_id == project_id
            ).first()
            print("🧱 DetailPart (Muro Base):", dp)
            if not dp:
                print("❌ No se encontró 'Muro Base'.")
                return None
            if "wall_id" in model_fields:
                data["wall_id"] = dp.id

        elif isinstance(enclosure_obj, RoofEnclosure):
            if project_id is None:
                print("❌ No hay project_id para 'Techo Base'.")
                return None
            dp = db.query(DetailPart).filter(
                DetailPart.name_detail == "Techo Base",
                DetailPart.project_id == project_id
            ).first()
            print("🏠 DetailPart (Techo Base):", dp)
            if not dp:
                print("❌ No se encontró 'Techo Base'.")
                return None
            if "roof_id" in model_fields:
                data["roof_id"] = dp.id

        elif isinstance(enclosure_obj, FloorEnclosure):
            if project_id is None:
                print("❌ No hay project_id para 'Piso Base'.")
                return None
            dp = db.query(DetailPart).filter(
                DetailPart.name_detail == "Piso Base",
                DetailPart.project_id == project_id
            ).first()
            print("🪵 DetailPart (Piso Base):", dp)
            if not dp:
                print("❌ No se encontró 'Piso Base'.")
                return None
            if "floor_id" in model_fields:
                data["floor_id"] = dp.id

        elif isinstance(enclosure_obj, WindowEnclosure):
            el = db.query(Element).filter(
                Element.name_element == "V Base",
                Element.type == "window"
            ).first()
            print("🪟 Element (V Base, window):", el)
            if not el:
                print("❌ No se encontró Element 'V Base' (type=window).")
                return None
            if "window_id" in model_fields:
                data["window_id"] = el.id

            if project_id is None:
                print("❌ No hay project_id para 'Muro Base' (housed_in).")
                return None
            dp = db.query(DetailPart).filter(
                DetailPart.name_detail == "Muro Base",
                DetailPart.project_id == project_id
            ).first()
            print("🧱 DetailPart (Muro Base) para housed_in:", dp)
            if not dp:
                print("❌ No se encontró 'Muro Base' para housed_in.")
                return None

            if "housed_in" in model_fields:
                data["housed_in"] = dp.id
            if "position" in model_fields:
                data["position"] = "Interior"
            if "with_no_return" in model_fields:
                data["with_no_return"] = "Sin"

        elif isinstance(enclosure_obj, DoorEnclosure):
            el = db.query(Element).filter(
                Element.name_element == "P Base",
                Element.type == "door"
            ).first()
            print("🚪 Element (P Base, door):", el)
            if not el:
                print("❌ No se encontró Element 'P Base' (type=door).")
                return None
            if "door_id" in model_fields:
                data["door_id"] = el.id

        else:
            print("❌ Tipo no soportado.")
            return None

        # 4) Defaults generales si existen
        if "angulo_azimut" in model_fields:
            data["angulo_azimut"] = DEFAULT_AZIMUTH
        if "orientation" in model_fields:
            data["orientation"] = DEFAULT_ORIENTATION
        if "is_base" in model_fields:
            data["is_base"] = True

        # 5) Referencia al original si existe
        if "original_id" in model_fields:
            src_id = getattr(enclosure_obj, "id", None)
            if src_id is not None:
                data["original_id"] = int(src_id)
                print(f"🔗 original_id -> {data['original_id']}")

        # 6) Crear y persistir clon
        print("🆕 Datos para nuevo registro:", data)
        clone = cls(**data)
        db.add(clone)
        db.commit()
        db.refresh(clone)
        print("✅ Clone creado:", clone)

        # 7) Post-procesos por tipo
        try:
            if isinstance(enclosure_obj, WallEnclosure):
                # Asegurar dp (Muro Base) y crear TBW
                if not dp:
                    dp = db.query(DetailPart).filter(
                        DetailPart.name_detail == "Muro Base",
                        DetailPart.project_id == project_id
                    ).first()
                    if not dp:
                        print("⚠️ No se pudo crear ThermalBridgeWall: no hay 'Muro Base'.")
                    else:
                        tbw = ThermalBridgeWall(
                            wall_id=clone.id,
                            enclosure_id=clone.enclosure_id,
                            po1_length=0, po2_length=0, po3_length=0, po4_length=0, po4_e_aislacion=0,
                            po1_id_element=dp.id, po2_id_element=dp.id, po3_id_element=dp.id, po4_id_element=dp.id,
                        )
                        db.add(tbw)
                        db.commit()
                        db.refresh(tbw)
                        print("🌡️ ThermalBridgeWall creado:", tbw)
                # Ejecutar cálculo de puentes térmicos de muro
                print("🧮 Ejecutando thermal_bridges_wall(...)")
                thermal_bridges_wall(clone, db)

            elif isinstance(enclosure_obj, WindowEnclosure):
                print("🧮 Ejecutando thermal_bridges_window(...)")
                thermal_bridges_window(clone, db)

            elif isinstance(enclosure_obj, RoofEnclosure):
                print("🧮 Ejecutando calculate_tablas_py('techo', ...)")
                calculate_tablas_py("techo", clone.id, clone.enclosure_id, db)

            elif isinstance(enclosure_obj, FloorEnclosure):
                print("🧮 Ejecutando floor(...) y calculate_termitancia_piso(...)")
                thermal_bridge_floor(clone, db)
                calculate_termitancia_piso(clone, db)

            elif isinstance(enclosure_obj, DoorEnclosure):
                print("🧮 Ejecutando calculate_tablas_py('door', ...)")
                calculate_tablas_py("door", clone.id, clone.enclosure_id, db)

        except Exception as post_e:
            # No romper el flujo por fallos de cálculo; loguear
            print(f"⚠️ Error en post-proceso de {cls.__name__}: {post_e}")

        return clone

    except Exception as e:
        db.rollback()
        print(f"💥 Error en create_obj_base: {e}")
        return None



def update_obj_base(
    original_obj: SpecificEnclosure,
    db: Session,
    *,
    copy_enclosure_id: bool = False
) -> Optional[List[int]]:
    """
    Propaga cambios del ORIGINAL a todos sus CLONES (mismo tipo) con original_id = original_obj.id.
    No toca los campos por defecto que fijamos al clonar.
    Después de actualizar cada clon, dispara los cálculos correspondientes al tipo.
    """
    try:
        if original_obj is None:
            print("❌ No se recibió el ORIGINAL.")
            return None

        cls: Type[SpecificEnclosure] = type(original_obj)
        if not hasattr(cls, "original_id"):
            print(f"❌ {cls.__name__} no tiene columna 'original_id'; no se puede sincronizar.")
            return None

        original_id = getattr(original_obj, "id", None)
        if original_id is None:
            print("❌ El ORIGINAL no tiene id.")
            return None

        print(f"📌 Sincronizando clones de {cls.__name__} original_id={original_id} ...")

        # Campos EXCLUIDOS (comunes)
        excluded = {"id", "is_base", "original_id", "angulo_azimut", "orientation"}
        if not copy_enclosure_id:
            excluded.add("enclosure_id")

        # Campos EXCLUIDOS por tipo
        if isinstance(original_obj, WallEnclosure):
            excluded.add("wall_id")
        elif isinstance(original_obj, RoofEnclosure):
            excluded.add("roof_id")
        elif isinstance(original_obj, FloorEnclosure):
            excluded.add("floor_id")
        elif isinstance(original_obj, WindowEnclosure):
            excluded.update({"window_id", "housed_in", "position", "with_no_return"})
        elif isinstance(original_obj, DoorEnclosure):
            excluded.add("door_id")

        model_fields = set(getattr(cls, "model_fields", {}).keys())

        # Buscar clones (solo base si existe el flag)
        q = db.query(cls).filter(cls.original_id == original_id)
        if hasattr(cls, "is_base"):
            q = q.filter(cls.is_base == True)
        clones: List[SpecificEnclosure] = q.all()
        print(f"🔎 Clones encontrados: {len(clones)} -> {[getattr(c, 'id', None) for c in clones]}")
        if not clones:
            print("ℹ️ No hay clones que sincronizar.")
            return []

        fields_to_copy = [f for f in model_fields if f not in excluded]
        print("🗂️ Campos a copiar:", fields_to_copy)

        updated_ids: List[int] = []
        for c in clones:
            before = {f: getattr(c, f, None) for f in fields_to_copy}
            for f in fields_to_copy:
                setattr(c, f, getattr(original_obj, f, None))
            after = {f: getattr(c, f, None) for f in fields_to_copy}
            print(f"\n🧩 Clone id={getattr(c, 'id', None)}")
            print("   ⬅️ Antes:", before)
            print("   ➡️  Después:", after)
            cid = getattr(c, "id", None)
            if cid is not None:
                updated_ids.append(cid)

        db.commit()
        print("✅ Commit realizado para sincronización de clones.")

        # Refresh y post-procesos por tipo
        for c in clones:
            db.refresh(c)

        # Ejecutar cálculos por cada clon actualizado (no romper por error de cálculo)
        for c in clones:
            try:
                if isinstance(c, WallEnclosure):
                    print(f"🧮 Recalc wall clone id={c.id} -> thermal_bridges_wall(...)")
                    thermal_bridges_wall(c, db)
                elif isinstance(c, WindowEnclosure):
                    print(f"🧮 Recalc window clone id={c.id} -> thermal_bridges_window(...)")
                    thermal_bridges_window(c, db)
                elif isinstance(c, RoofEnclosure):
                    print(f"🧮 Recalc roof clone id={c.id} -> calculate_tablas_py('techo', ...)")
                    calculate_tablas_py("techo", c.id, c.enclosure_id, db)
                elif isinstance(c, FloorEnclosure):
                    print(f"🧮 Recalc floor clone id={c.id} -> floor(...) + calculate_termitancia_piso(...)")
                    thermal_bridge_floor(c, db)
                    calculate_termitancia_piso(c, db)
                elif isinstance(c, DoorEnclosure):
                    print(f"🧮 Recalc door clone id={c.id} -> calculate_tablas_py('door', ...)")
                    calculate_tablas_py("door", c.id, c.enclosure_id, db)
            except Exception as post_e:
                print(f"⚠️ Error en post-proceso de {type(c).__name__} (id={getattr(c,'id',None)}): {post_e}")

        print("🎯 Clones sincronizados:", updated_ids)
        return updated_ids

    except Exception as e:
        db.rollback()
        print(f"💥 Error en sync_clones_from_original_debug: {e}")
        return None
    
    

def delete_obj_base(original_obj: SpecificEnclosure, db: Session) -> Optional[Dict[str, Any]]:
    """
    Elimina (HARD DELETE) todos los clones del objeto original recibido:
    - Busca en la MISMA tabla registros con original_id = original_obj.id
    - Si es WallEnclosure, borra también ThermalBridgeWall de cada clon (wall_id = clone.id)
    - No toca el registro original
    Retorna un resumen con conteos e ids borrados.
    """
    try:
        if original_obj is None:
            print("❌ No se recibió el objeto ORIGINAL.")
            return None

        cls: Type[SpecificEnclosure] = type(original_obj)
        original_id = getattr(original_obj, "id", None)
        print(f"📌 Eliminar clones de ORIGINAL {cls.__name__} id={original_id}")

        if original_id is None:
            print("❌ El ORIGINAL no tiene id.")
            return None

        # Verificación mínima de esquema
        if not hasattr(cls, "original_id"):
            print(f"❌ {cls.__name__} no tiene columna 'original_id'.")
            return None

        # Si existe is_base, lo usamos para garantizar que solo borremos clones/base
        has_is_base = hasattr(cls, "is_base")

        q = db.query(cls).filter(cls.original_id == original_id)
        if has_is_base:
            q = q.filter(cls.is_base == True)

        clones: List[SpecificEnclosure] = q.all()
        print(f"🔎 Clones encontrados: {len(clones)} -> {[getattr(c, 'id', None) for c in clones]}")

        if not clones:
            print("ℹ️ No hay clones para este original.")
            return {"deleted_count": 0, "deleted_clone_ids": [], "deleted_tbw_ids": []}

        deleted_clone_ids: List[int] = []
        deleted_tbw_ids: List[int] = []

        # Si es wall, primero borro ThermalBridgeWall de cada clon
        if issubclass(cls, WallEnclosure) or isinstance(original_obj, WallEnclosure):
            for c in clones:
                wall_id = getattr(c, "id", None)
                if wall_id is None:
                    continue
                tbws = (
                    db.query(ThermalBridgeWall)
                      .filter(ThermalBridgeWall.wall_id == wall_id)
                      .all()
                )
                if tbws:
                    print(f"🌡️ TBW asociados a clone wall_id={wall_id}: {[t.id for t in tbws]}")
                    for t in tbws:
                        deleted_tbw_ids.append(t.id)
                        db.delete(t)

        # Ahora borro los clones
        for c in clones:
            cid = getattr(c, "id", None)
            if cid is not None:
                deleted_clone_ids.append(cid)
            db.delete(c)

        db.commit()
        print("✅ Commit realizado.")
        return {
            "deleted_count": len(deleted_clone_ids),
            "deleted_clone_ids": deleted_clone_ids,
            "deleted_tbw_ids": deleted_tbw_ids
        }

    except Exception as e:
        db.rollback()
        print(f"💥 Error al borrar clones de {type(original_obj).__name__}: {e}")
        return None
    
    

