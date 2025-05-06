import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useGlobal } from '../../states/GlobalState';

const PropHistory = () => {
    const bottomRef = useRef(null);
    const { requestMsg, responseMsg, isConnected } = useGlobal();

    // Conversation history state
    const [conversation, setConversation] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(false);

    const avatarUrl = '/Archi.ai.png';

    // Handle new user messages
    useEffect(() => {
        if (requestMsg && requestMsg.trim() !== '') {
            setConversation(prev => [...prev, {
                type: 'user',
                content: requestMsg
            }]);
            setIsLoading(true);
        }
    }, [requestMsg]);

    // Handle AI responses
    useEffect(() => {
        if (responseMsg && responseMsg.trim() !== '') {
            setIsLoading(false);
            // Format the response (remove "AI Response: " prefix if present)
            const formattedResponse = responseMsg.replace(/^AI Response: /, '');
            setConversation(prev => [...prev, {
                type: 'ai',
                content: formattedResponse
            }]);
        }
    }, [responseMsg]);

    // Scroll to bottom when conversation updates
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [conversation, isLoading]);

    // Display connection status
    const ConnectionStatus = () => (
        <div className={`absolute top-2 right-2 flex items-center ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-xs">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
    );

    return (
        <div className="flex flex-col h-full py-4 px-2 overflow-y-auto no-scrollbar relative">
            <ConnectionStatus />

            {conversation.length === 0 && (
                <div className="flex items-center justify-center h-full text-gray-400">
                    <p>Start a conversation with Archi.ai</p>
                </div>
            )}

            {conversation.map((msg, index) => (
                <div key={index} className={`flex w-full mb-4 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex p-4 rounded-lg max-w-[80%] ${
                        msg.type === 'user'
                            ? 'bg-gray-400/10 text-white'
                            : 'bg-slate-900/80 text-white'
                    }`}>
                        {msg.type === 'ai' && (
                            <img src={avatarUrl} alt="Avatar" className="w-8 h-8 mr-4 rounded-full" />
                        )}
                        <div className="whitespace-pre-wrap">
                            {msg.content}
                        </div>
                    </div>
                </div>
            ))}

            {isLoading && (
                <div className="flex justify-start mb-4">
                    <div className="flex p-4 rounded-lg bg-slate-900/80 text-white">
                        <img src={avatarUrl} alt="Avatar" className="w-8 h-8 mr-4 rounded-full" />
                        <motion.div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0s]"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                        </motion.div>
                    </div>
                </div>
            )}

            <div ref={bottomRef} />
        </div>
    );
};

export default PropHistory;