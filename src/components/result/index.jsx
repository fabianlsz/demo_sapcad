import React, { useState, useRef } from "react";
import IfcViewer from "./IfcViewer";
import NeonButton from "../general/NeonButton";

const Result = () => {
    const [ifcFile, setIfcFile] = useState(null);

    const handleClick = () => {
        fileInputRef.current?.click(); // simulate click on hidden input
    };
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setIfcFile(file);
    };
    const fileInputRef = useRef(null);

    return (
        <div className="w-full h-full p-4 flex flex-col">
            <div>
                <input
                    type="file"
                    accept=".ifc"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                    className="hidden"
                />

                <NeonButton onClick={handleClick}>
                    Upload IFC File
                </NeonButton>
            </div>
            <IfcViewer file={ifcFile} />
        </div>
    );
};

export default Result;