import ifcopenshell
import ifcopenshell.util.element as element_util
import ifcopenshell.geom
import os
import json
import uuid
from datetime import datetime

# Set up IFC settings
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

def process_ifc_file(file_path: str):
    """
    Parse and extract metadata from the IFC file.
    Returns detailed information about the model's entities.
    """
    try:
        # Open the IFC file
        model = ifcopenshell.open(file_path)

        # Basic metadata
        project = model.by_type("IfcProject")[0]
        metadata = {
            "ProjectName": project.Name if project.Name else "Unnamed Project",
            "ProjectDescription": project.Description if project.Description else "No description",
            "FileName": os.path.basename(file_path),
            "FilePath": file_path,
            "EntityCounts": {}
        }

        # Extract entities and count them by type
        entity_types = ["IfcWall", "IfcWindow", "IfcDoor", "IfcSlab", "IfcRoof",
                        "IfcColumn", "IfcBeam", "IfcStair", "IfcSpace", "IfcFurnishingElement"]

        entity_details = {}

        for entity_type in entity_types:
            entities = model.by_type(entity_type)
            metadata["EntityCounts"][entity_type] = len(entities)

            # Get details for each entity
            if entities:
                entity_details[entity_type] = []
                for entity in entities:
                    entity_info = {
                        "GlobalId": entity.GlobalId,
                        "Name": entity.Name if hasattr(entity, "Name") and entity.Name else f"{entity_type}_{entity.id()}",
                        "id": entity.id()
                    }

                    # Try to get material information
                    try:
                        materials = element_util.get_material(entity)
                        if materials:
                            if hasattr(materials, "Name"):
                                entity_info["Material"] = materials.Name
                            elif isinstance(materials, list):
                                entity_info["Materials"] = [m.Name for m in materials if hasattr(m, "Name")]
                    except:
                        pass

                    # Try to get color information if available
                    try:
                        styles = element_util.get_style(entity)
                        if styles and hasattr(styles, "Styles"):
                            for style in styles.Styles:
                                if style.is_a("IfcSurfaceStyle"):
                                    for style_item in style.Styles:
                                        if style_item.is_a("IfcSurfaceStyleShading"):
                                            entity_info["Color"] = {
                                                "Red": style_item.SurfaceColour.Red,
                                                "Green": style_item.SurfaceColour.Green,
                                                "Blue": style_item.SurfaceColour.Blue,
                                                "Alpha": style_item.SurfaceColour.Alpha if hasattr(style_item.SurfaceColour, "Alpha") else 1.0
                                            }
                    except:
                        pass

                    # Get properties
                    try:
                        props = element_util.get_psets(entity)
                        if props:
                            entity_info["Properties"] = props
                    except:
                        pass

                    entity_details[entity_type].append(entity_info)

        metadata["EntityDetails"] = entity_details
        return metadata
    except Exception as e:
        return {"error": str(e)}

def modify_ifc_entities(file_path: str, modification_data: dict):
    """
    Modify IFC entities based on the modification data.

    Args:
        file_path: Path to the IFC file
        modification_data: Dictionary with modification instructions

    Returns:
        Path to the modified file and a summary of changes
    """
    try:
        # Open the IFC file
        model = ifcopenshell.open(file_path)

        # Extract modification parameters
        entity_type = modification_data.get("entity_type", "")
        entity_ids = modification_data.get("entity_ids", ["all"])
        property_to_modify = modification_data.get("property", "")
        new_value = modification_data.get("new_value", "")

        # Check if we have valid data
        if not entity_type or not property_to_modify or not new_value:
            return {"error": "Missing required modification parameters"}

        # Get entities to modify
        if entity_type == "unknown":
            return {"error": "Could not determine which entity type to modify"}

        entities = model.by_type(entity_type)

        # Filter entities by ID if specific IDs are provided
        if entity_ids != ["all"]:
            try:
                entity_ids = [int(id) for id in entity_ids if str(id).isdigit()]
                entities = [e for e in entities if e.id() in entity_ids]
            except:
                # If conversion fails, proceed with all entities
                pass

        if not entities:
            return {"error": f"No {entity_type} entities found to modify"}

        changes_made = 0

        # Apply modifications based on property type
        if property_to_modify.lower() in ["color", "colour"]:
            # Handle color modification
            changes_made = _modify_entity_colors(model, entities, new_value)

        elif property_to_modify.lower() in ["material"]:
            # Handle material modification
            changes_made = _modify_entity_materials(model, entities, new_value)

        elif property_to_modify.lower() in ["name"]:
            # Handle name modification
            for entity in entities:
                if hasattr(entity, "Name"):
                    entity.Name = new_value
                    changes_made += 1

        # Save the modified file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)
        output_dir = os.path.join(os.path.dirname(file_path), "modified")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, f"{base_name}_modified_{timestamp}{ext}")
        model.write(output_path)

        return {
            "original_file": file_path,
            "modified_file": output_path,
            "entities_modified": changes_made,
            "modification": {
                "entity_type": entity_type,
                "property": property_to_modify,
                "new_value": new_value
            }
        }

    except Exception as e:
        return {"error": str(e)}

def _modify_entity_colors(model, entities, color_value):
    """Helper function to modify entity colors"""
    changes_made = 0
    try:
        # Parse color value
        if isinstance(color_value, str):
            color_name = color_value.lower()
            # Map of color names to RGB values
            color_map = {
                "red": (1.0, 0.0, 0.0),
                "green": (0.0, 1.0, 0.0),
                "blue": (0.0, 0.0, 1.0),
                "yellow": (1.0, 1.0, 0.0),
                "white": (1.0, 1.0, 1.0),
                "black": (0.0, 0.0, 0.0),
                "gray": (0.5, 0.5, 0.5),
                "purple": (0.5, 0.0, 0.5),
                "orange": (1.0, 0.65, 0.0),
                "brown": (0.65, 0.16, 0.16)
            }
            if color_name in color_map:
                r, g, b = color_map[color_name]
            else:
                # Default to red if color not recognized
                r, g, b = (1.0, 0.0, 0.0)
        else:
            # Default to red
            r, g, b = (1.0, 0.0, 0.0)

        # Create a new color
        rgb = model.createIfcColourRgb(None, r, g, b)

        # Create surface style shading
        surface_shading = model.createIfcSurfaceStyleShading(rgb)

        # Create surface style rendering
        renderer = model.createIfcSurfaceStyleRendering(
            rgb, 0.0, None, None, None, None, None, None, "FLAT"
        )

        # Create surface style
        style_name = f"Color-{uuid.uuid4().hex[:8]}"
        surface_style = model.createIfcSurfaceStyle(
            style_name, "BOTH", [surface_shading, renderer]
        )

        # Create presentation style assignment
        style_assignment = model.createIfcPresentationStyleAssignment([surface_style])

        # Apply styling to each entity
        for entity in entities:
            # Get entity representation
            if hasattr(entity, "Representation") and entity.Representation:
                representations = entity.Representation.Representations

                for rep in representations:
                    for item in rep.Items:
                        # Create styled item
                        styled_item = model.createIfcStyledItem(item, [style_assignment], None)
                        changes_made += 1

        return changes_made
    except Exception as e:
        print(f"Error modifying colors: {e}")
        return changes_made

def _modify_entity_materials(model, entities, material_name):
    """Helper function to modify entity materials"""
    changes_made = 0
    try:
        # Create a new material if it doesn't exist
        materials = model.by_type("IfcMaterial")
        material = None

        # Try to find existing material with the same name
        for mat in materials:
            if mat.Name == material_name:
                material = mat
                break

        # Create new material if not found
        if not material:
            material = model.createIfcMaterial(material_name)

        # Create material assignment for each entity
        for entity in entities:
            # Create material select
            material_select = model.createIfcMaterialDefinitionRepresentation(
                material_name, None, None, material
            )

            # Assign material to entity
            rel = model.createIfcRelAssociatesMaterial(
                ifcopenshell.guid.new(),  # GlobalId
                model.by_type("IfcOwnerHistory")[0] if model.by_type("IfcOwnerHistory") else None,  # OwnerHistory
                f"MaterialAssignment-{material_name}",  # Name
                None,  # Description
                [entity],  # RelatedObjects
                material  # RelatingMaterial
            )
            changes_made += 1

        return changes_made
    except Exception as e:
        print(f"Error modifying materials: {e}")
        return changes_made

def get_entity_summary(file_path: str):
    """
    Get a simplified summary of IFC entities suitable for AI context.
    """
    try:
        model = ifcopenshell.open(file_path)

        # Create a summary of the model contents
        summary = []
        summary.append(f"IFC File: {os.path.basename(file_path)}")

        # Project info
        projects = model.by_type("IfcProject")
        if projects:
            project = projects[0]
            summary.append(f"Project: {project.Name or 'Unnamed'}")

        # Count entities by type
        entity_types = ["IfcWall", "IfcWindow", "IfcDoor", "IfcSlab", "IfcRoof",
                        "IfcColumn", "IfcBeam", "IfcStair", "IfcSpace", "IfcFurnishingElement"]

        counts = {}
        for entity_type in entity_types:
            count = len(model.by_type(entity_type))
            if count > 0:
                counts[entity_type] = count

        # Add counts to summary
        summary.append("Entity counts:")
        for entity_type, count in counts.items():
            summary.append(f"- {entity_type}: {count} elements")

        # Sample materials
        materials = model.by_type("IfcMaterial")
        if materials:
            summary.append("\nSample materials:")
            for i, material in enumerate(materials[:5]):  # Show up to 5 materials
                summary.append(f"- {material.Name}")
            if len(materials) > 5:
                summary.append(f"  (and {len(materials) - 5} more materials)")

        return "\n".join(summary)
    except Exception as e:
        return f"Error getting entity summary: {str(e)}"