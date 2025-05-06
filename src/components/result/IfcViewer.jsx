import React, { useRef, useEffect, useState } from 'react';
import { IfcViewerAPI } from 'web-ifc-viewer';
import { useGlobal } from '../../states/GlobalState';

const IfcViewer = ({ file }) => {
    const containerRef = useRef(null);
    const viewerRef = useRef(null);
    const [parsedEntities, setParsedEntities] = useState(null);
    const { setIfcData, responseMsg } = useGlobal();

    // Initialize viewer
    useEffect(() => {
        const container = containerRef.current;

        if (!viewerRef.current && container) {
            const viewer = new IfcViewerAPI({
                container,
                backgroundColor: new Uint8ClampedArray([255, 255, 255, 255])
            });
            viewerRef.current = viewer;
            viewer.IFC.setWasmPath('/wasm/');
        }
    }, []);

    // Handle file loading
    useEffect(() => {
        const loadIfc = async () => {
            if (file && viewerRef.current) {
                try {
                    console.log("Loading IFC file...");
                    const url = URL.createObjectURL(file);

                    // Upload file to backend
                    const formData = new FormData();
                    formData.append('file', file);

                    const uploadResponse = await fetch('/upload/', {
                        method: 'POST',
                        body: formData,
                    });

                    const uploadData = await uploadResponse.json();
                    console.log("Upload response:", uploadData);

                    // Store metadata in global state
                    if (uploadData.metadata && !uploadData.error) {
                        setIfcData({
                            filename: file.name,
                            ...uploadData.metadata,
                            entities: uploadData.entities || []
                        });
                        setParsedEntities(uploadData.entities || []);
                    }

                    // Load the model in the viewer
                    const model = await viewerRef.current.IFC.loadIfcUrl(url);
                    console.log("IFC file loaded successfully.");

                    // Set the position of the model
                    model.position.set(0, 0, 0);
                    viewerRef.current.context.scene.add(model);

                    // Adjust the camera to fit the model
                    viewerRef.current.context.fitToFrame();
                } catch (err) {
                    console.error("Failed to load IFC file:", err);
                }
            }
        };

        loadIfc();
    }, [file, setIfcData]);

    // Handle model modifications based on AI response
    useEffect(() => {
        const applyChanges = async () => {
            if (responseMsg && responseMsg.includes('modification_applied') && file) {
                try {
                    // Reload the model to show updated version
                    const refreshFormData = new FormData();
                    refreshFormData.append('action', 'refresh');
                    refreshFormData.append('filename', file.name);

                    const refreshResponse = await fetch('/refresh_model/', {
                        method: 'POST',
                        body: refreshFormData,
                    });

                    if (refreshResponse.ok) {
                        const blob = await refreshResponse.blob();
                        const newFile = new File([blob], file.name, { type: file.type });

                        // Reload the model with updated file
                        const url = URL.createObjectURL(newFile);
                        viewerRef.current.IFC.reset();
                        const model = await viewerRef.current.IFC.loadIfcUrl(url);
                        model.position.set(0, 0, 0);
                        viewerRef.current.context.scene.add(model);
                        viewerRef.current.context.fitToFrame();

                        console.log("Model refreshed with applied changes");
                    }
                } catch (err) {
                    console.error("Failed to refresh model:", err);
                }
            }
        };

        applyChanges();
    }, [responseMsg, file]);

    return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />;
};

export default IfcViewer;