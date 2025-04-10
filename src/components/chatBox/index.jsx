import React, { useState, useEffect } from "react";
import Form from "./form";
import PropHistory from "./propHistory";
import { useGlobal } from '../../states/GlobalState';

const ChatBox = () => {
    const [messages, setMessages] = useState([]);
    const { requestMsg, } = useGlobal();
    const avatarUrl = '/Archi.ai.png';

    useEffect(() => {
        if (requestMsg !== "")
            setMessages([...messages, `${requestMsg}`]);
    }, [requestMsg])

    const handleMessageSend = (message) => {
        const aiResponse = `AI Response to: ${message}`;
        setMessages([...messages, aiResponse]);
    };

    return (
        <div className="w-full h-full p-4 flex flex-col">
            <div className=" bg-black text-white bg-diagonal-stripes">
                <div className=" z-10 p-6">
                    <h1 className="text-3xl font-semibold">SAPCAD</h1>
                    <p className="text-gray-400">Precision architectural modeling & AI-driven design.</p>
                </div>
            </div>
            <PropHistory messages={messages} avatar={avatarUrl} />
            <Form onSend={handleMessageSend} />
        </div>
    );
};

export default ChatBox;