import React from "react";
import Form from "./form";
import PropHistory from "./propHistory";
import { useGlobal } from '../../states/GlobalState';

const ChatBox = () => {
    const { ifcData } = useGlobal();

    return (
        <div className="w-full h-full flex flex-col">
            <div className="bg-black text-white bg-diagonal-stripes">
                <div className="z-10 p-6">
                    <h1 className="text-3xl font-semibold">SAPCAD</h1>
                    <p className="text-gray-400">Precision architectural modeling & AI-driven design.</p>
                </div>
            </div>

            {ifcData && (
                <div className="px-4 py-2 bg-gray-800/50 backdrop-blur-md">
                    <p className="text-sm text-cyan-400">
                        Working with: <span className="font-medium">{ifcData.filename}</span>
                    </p>
                </div>
            )}

            <div className="flex-grow overflow-hidden">
                <PropHistory />
            </div>

            <Form />
        </div>
    );
};

export default ChatBox;