import React, { useState, useRef, useEffect } from 'react';
import { useGlobal } from '../../states/GlobalState';
import NeonButton from '../general/NeonButton';

const Form = () => {
    const [message, setMessage] = useState('');
    const { setRequestMsg, isConnected, ifcData } = useGlobal();
    const textareaRef = useRef(null);

    // Auto-resize the textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [message]);

    const handleSend = (e) => {
        e.preventDefault();
        if (message.trim() === '') return;

        setRequestMsg(message);
        setMessage('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend(e);
        }
    };

    return (
        <div className='flex w-full'>
            <form
                onSubmit={handleSend}
                className="flex w-full bottom-0 left-0 right-0 bg-transparent p-4 no-scrollbar overscroll-auto"
            >
                <div className="max-w-2xl w-full mx-auto flex items-end gap-2">
                    <textarea
                        ref={textareaRef}
                        rows={1}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={ifcData ? "Ask about your IFC model..." : "Message Archi.ai"}
                        className="w-full resize-none rounded-lg p-3 text-white bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
                        disabled={!isConnected}
                    />
                    <NeonButton
                        type="submit"
                        disabled={!isConnected}
                        className={!isConnected ? 'opacity-50 cursor-not-allowed' : ''}
                    >
                        Send
                    </NeonButton>
                </div>
            </form>
        </div>
    );
};

export default Form;