import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";

const PropHistory = ({ messages, avatar }) => {
    const bottomRef = useRef(null);
    const [isThinking, setIsThinking] = useState(true);
    const [showAnswer, setShowAnswer] = useState(false);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        const thinkingTimer = setTimeout(() => {
            setIsThinking(false);
            setShowAnswer(true);
        }, 1000);
        return () => clearTimeout(thinkingTimer);
    }, [messages]);

    return (
        <div className="flex flex-col h-full p-4 overflow-y-auto no-scrollbar">
            {messages.map((msg, index) => (
                <div key={index} className="flex flex-col w-full ">
                    <div className="flex flex-rows float-right items-center mb-4 p-4 bg-gray-400/10 text-white rounded-lg">
                        {msg}
                    </div>
                    {index < 3 &&
                        <div className="flex flex-rows left items-center mb-4 p-4 bg-slate-900/80 text-white rounded-lg">
                            <img src={avatar} alt="Avatar" className="w-8 h-8 mr-4 rounded-full" />
                            {isThinking && (
                                <div>
                                    <div className="p-4 rounded-xl shadow text-gray-600 flex items-center space-x-2">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0s]"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                                    </div>
                                </div>
                            )}
                            {showAnswer && (
                                <motion.div
                                    initial={{ opacity: 0, y: 0 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 1, duration: 0.05 }}
                                >
                                    {index === 0 ? "Hello, how can I help you" : index === 1 ? "Sure, it's my pleasure to help you." : "No problem"}

                                </motion.div>
                            )}
                        </div>

                    }
                    <div ref={bottomRef} />

                </div>
            ))}
        </div>
    );
};

export default PropHistory;