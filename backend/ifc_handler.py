import ifcopenshell

def process_ifc_file(file_path: str):
    """
    Parse and extract metadata from the IFC file.
    Modify the file if needed.
    """
    try:
        # Open the IFC file
        model = ifcopenshell.open(file_path)

        # Example: Extract some metadata
        project = model.by_type("IfcProject")[0]
        metadata = {
            "ProjectName": project.Name,
            "ProjectDescription": project.Description
        }

        # Example modification (Not saved to file for now)
        for wall in model.by_type("IfcWall"):
            wall.Name = "Modified Wall"

        return metadata
    except Exception as e:
        return {"error": str(e)}