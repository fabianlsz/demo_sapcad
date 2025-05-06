import React, { useState, useRef } from "react";
import IfcViewer from "./IfcViewer";
import NeonButton from "../general/NeonButton";
import { useGlobal } from "../../states/GlobalState";

const Result = () => {
    const [ifcFile, setIfcFile] = useState(null);
    const { ifcData } = useGlobal();
    const fileInputRef = useRef(null);

    const handleClick = () => {
        fileInputRef.current?.click(); // simulate click on hidden input
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.name.toLowerCase().endsWith('.ifc')) {
            setIfcFile(file);
        } else {
            alert("Please select a valid IFC file");
        }
    };

    return (
        <div className="w-full h-full flex flex-col">
            <div className="p-4 flex justify-between items-center">
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

                {ifcFile && (
                    <div className="text-white">
                        <p className="font-medium">{ifcFile.name}</p>
                    </div>
                )}
            </div>

            {ifcData && (
                <div className="p-4 bg-gray-800/50 backdrop-blur-md rounded-lg mb-4 text-white">
                    <h3 className="text-xl mb-2">Project Information</h3>
                    <p><span className="font-medium">Name:</span> {ifcData.ProjectName || 'N/A'}</p>
                    <p><span className="font-medium">Description:</span> {ifcData.ProjectDescription || 'N/A'}</p>

                    {ifcData.entities && ifcData.entities.length > 0 && (
                        <div className="mt-3">
                            <h4 className="text-lg mb-1">Entities:</h4>
                            <div className="grid grid-cols-3 gap-2">
                                {ifcData.entities.map((entity, index) => (
                                    <div key={index} className="flex items-center">
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full mr-2"></span>
                                        <span>{entity.type}: {entity.count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            <div className="flex-grow">
                <IfcViewer file={ifcFile} />
            </div>
        </div>
    );
};

export default Result;