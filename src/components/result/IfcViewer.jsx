import React, { useRef, useEffect } from 'react';
import { IfcViewerAPI } from 'web-ifc-viewer';

const IfcViewer = ({ file }) => {
    const containerRef = useRef(null);
    const viewerRef = useRef(null);

    useEffect(() => {
        const container = containerRef.current;

        if (!viewerRef.current && container) {
            const viewer = new IfcViewerAPI({ container, backgroundColor: new Uint8ClampedArray([255, 255, 255, 255]) });
            viewerRef.current = viewer;
            // viewer.grid.setGrid(); //if you want grid decomment this line
            // viewer.axes.setAxes(); //if you want grid decomment this line
            viewer.IFC.setWasmPath('/wasm/'); // Correct relative path
        }
    }, []);

    useEffect(() => {
        const loadIfc = async () => {
            if (file && viewerRef.current) {
                try {
                    console.log("Loading IFC file...");
                    const url = URL.createObjectURL(file);
                    const model = await viewerRef.current.IFC.loadIfcUrl(url);
                    console.log("IFC file loaded successfully.");

                    // Set the position of the model
                    model.position.set(0, 0, 0); // Adjust the coordinates as needed
                    viewerRef.current.context.scene.add(model);

                    // Adjust the camera to fit the model
                    viewerRef.current.context.fitToFrame();
                } catch (err) {
                    console.error("Failed to load IFC file:", err);
                }
            }

        };

        loadIfc();
    }, [file]);

    return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />;
};

export default IfcViewer;